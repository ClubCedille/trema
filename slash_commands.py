import asyncio
from datetime import datetime
from discord import\
	Color,\
	Embed,\
	Option,\
	SlashCommandGroup,\
	utils,\
	File

from discord.ext import commands

from prompts import\
	prompt_user,\
	prompt_user_with_confirmation,\
	prompt_user_with_date,\
	prompt_for_image

from text_format import\
	_make_cmd_full_name,\
	make_mention,\
	generate_mention_dict,\
	_make_config_confirm_embed,\
	_make_config_display_embed,\
	_make_config_error_embed

from discord_util import\
	get_channel_name

from discord_util import\
	send_delayed_dm


from text_format import\
	make_mention,\
	generate_mention_dict

from uuid import uuid4

_MEMBER_MENTIONABLE = "[@-]"
_REQUEST_VALUE = "$"
_SPACE = " "

def generate_unique_webhook_url():
    return str(uuid4())

def is_authorized(trema_db):
	async def predicate(ctx):
		admin_role_id = trema_db.get_server_admin_role(ctx.guild.id)
		isAllowed = ctx.author.id == ctx.guild.owner_id or any(role.id == admin_role_id for role in ctx.author.roles)

		if not isAllowed:
			admin_role = ctx.guild.get_role(admin_role_id)
			admin_role_name = 'Owner' if admin_role is None else admin_role.name
			embed_error = _make_config_error_embed(
				"Manque de permission",
				ctx.command,
				f"Vous n'êtes pas autorisé à utiliser cette commande. Le rôle {admin_role_name} est requis."
			)
			await ctx.respond(embed=embed_error, ephemeral=True)
		return isAllowed
	return commands.check(predicate)

def create_slash_cmds(trema_bot, trema_db, start_time):
	config = _create_config_cmds(trema_db)
	_create_config_reminder_cmds(trema_db, config)
	_create_information_cmds(trema_bot, start_time)
	_create_management_cmds(trema_bot, trema_db)
	webhook = _create_webhooks_cmds(trema_db)
	trema_bot.add_application_command(config)
	trema_bot.add_application_command(webhook)

def _create_config_cmds(trema_db):
	config = SlashCommandGroup(name="config",
		description="Configurez les options de Trëma pour votre serveur.")

	@config.command(name="adminrole",
		description="Configurer le rôle d'administrateur de Trëma pour ce serveur.")
	async def config_admin_role(ctx,
			role_id: Option(str, "L'ID du rôle d'administrateur ou 'None' pour retirer le rôle.")):

		guild_id = ctx.guild_id
		guild = ctx.guild
		owner_id = guild.owner_id
		embed_title = _make_cmd_full_name(ctx.command) + _SPACE + str(role_id)

		# Get previous value from the database
		prev_role_id = trema_db.get_server_admin_role(guild_id)
		prev_role_name = guild.get_role(prev_role_id)
		prev_value = f"{prev_role_name} ({prev_role_id})" if prev_role_name else 'Owner'

		# Check if the user is the owner of the server
		if ctx.author.id != owner_id:
			error_embed = _make_config_error_embed(embed_title, prev_value,
				"Seul le propriétaire du serveur peut changer ce rôle.")
			await ctx.respond(embed=error_embed, ephemeral=True)
			return

		if role_id.lower() == "none":  # Check if the user wants to remove the admin role
			trema_db.set_server_admin_role(guild_id, None)
			response_embed = _make_config_confirm_embed(
				embed_title, 'Owner', prev_value)
			await ctx.respond(embed=response_embed, ephemeral=True)
			return

		try:
			role_id = int(role_id)
		except ValueError:
			error_embed = _make_config_error_embed(embed_title, prev_value,
													f"{role_id} n'est pas un ID de rôle valide ou 'None'.")
			await ctx.respond(embed=error_embed, ephemeral=True)
			return
		
		# Check if the role exists in the server
		role = guild.get_role(role_id)
		if role is None:
			error_embed = _make_config_error_embed(embed_title, prev_value,
				f"Le rôle avec l'ID {role_id} n'existe pas dans ce serveur.")
			await ctx.respond(embed=error_embed, ephemeral=True)
			return

		# All checks passed, update the value in the database
		trema_db.set_server_admin_role(guild_id, role_id)
		confirmed_role_id = trema_db.get_server_admin_role(guild_id)
		confirmed_role_name = guild.get_role(confirmed_role_id).name
		updated_value = f"{confirmed_role_name} ({confirmed_role_id})"
		response_embed = _make_config_confirm_embed(
			embed_title, updated_value, prev_value)

		await ctx.respond(embed=response_embed, ephemeral=True)
	
	@config.command(name="aide",
		description="Informations sur les commandes /config")
	async def aide(ctx):

		embed_title = _make_cmd_full_name(ctx.command)
		instructions =\
			"Le groupe de commandes **/config** permet de changer les paramètres de Trëma. "\
			+ "Écrivez **/config** dans le champ des messages pour voir les paramètres "\
			+ "disponibles et leur description.\n\n"\
			+ "Donnez l'argument **$** à une commande **/config** pour voir la valeur actuelle "\
			+ "d'un paramètre.\n\n"\
			+ "Certains paramètres sont des messages affichés arpès un évènement concernant "\
			+ "un membre particulier. Pour mentionner ce membre, écrivez **@-** dans ces messages. "\
			+ "Le signe **[@-]** au début d'une description inidque que cette action est possible."
		help_embed = Embed(
			title=embed_title,
			description=instructions,
			color=Color.blue())
		await ctx.respond(embed=help_embed, ephemeral=True)


	@config.command(name="canalaccueil",
		description="Changer le canal d'accueil des nouveaux membres")
	@is_authorized(trema_db)
	async def config_welcome_chan(ctx,
			id_accueil: Option(str,
			"Identifiant du canal où les nouveaux membres reçoivent le message d'accueil")):

		guild = ctx.guild
		guild_id = ctx.guild_id
		embed_title = _make_cmd_full_name(ctx.command) + _SPACE + id_accueil

		prev_value = trema_db.get_server_welcome_chan_id(guild_id)
		welcome_chan_name = get_channel_name(guild, prev_value)
		prev_value = f"{welcome_chan_name} ({prev_value})"

		try:
			# The command argument is a string.
			id_accueil = int(id_accueil)
			selected_chan = guild.get_channel(id_accueil)

		except ValueError:
			pass

		if isinstance(id_accueil, str) and id_accueil == _REQUEST_VALUE:
			response_embed = _make_config_display_embed(embed_title, prev_value)

		elif not isinstance(id_accueil, int) or id_accueil < 0:
			response_embed = _make_config_error_embed(embed_title, prev_value,
				"L'identifiant des canaux est un nombre entier positif.")

		elif selected_chan is None:
			response_embed = _make_config_error_embed(embed_title, prev_value,
				f"{guild.name} n'a pas de canal {id_accueil}.")

		else:
			trema_db.set_server_welcome_chan_id(guild_id, id_accueil)
			confirmed_chan_id = trema_db.get_server_welcome_chan_id(guild_id)
			confirmed_chan_name = guild.get_channel(confirmed_chan_id).name
			updated_value = f"{confirmed_chan_name} ({confirmed_chan_id})"
			response_embed = _make_config_confirm_embed(
				embed_title, updated_value, prev_value)

		await ctx.respond(embed=response_embed, ephemeral=True)

	@config.command(name="msgaccueil",
		description=f"{_MEMBER_MENTIONABLE} Changer le message affiché lorsqu'un membre arrive dans le serveur")
	@is_authorized(trema_db)
	async def config_welcome_msg(ctx):
		
		guild_id = ctx.guild_id
		prev_value = trema_db.get_server_welcome_msg(guild_id)
		
		await ctx.respond("Veuillez vérifier vos messages privés pour des instructions supplémentaires.", ephemeral=True)
		
		user = ctx.author
		dm_channel = user.dm_channel
		if dm_channel is None:
			dm_channel = await user.create_dm()
			
		embed = Embed(
			title="Configuration du message d'accueil",
			description=f"Le message d'accueil actuel est: `{prev_value}`\n\n"
						"Pour personnaliser ce message, vous pouvez utiliser les mentions suivantes:\n"
						"- `{member}` pour mentionner le nouveau membre\n"
						"- `{username}` pour mentionner un username\n"
						"- `{server}` pour le nom du serveur\n"
						"- `{&role}` pour mentionner un rôle par son nom\n"
						"- `{#channel}` pour un lien vers un canal\n"
						"- `{everyone}` pour `@everyone`\n"
						"- `{here}` pour `@here`\n\n"
						"Veuillez entrer le nouveau message d'accueil.",
			color=Color.blue()
		)
		
		await dm_channel.send(embed=embed)
		
		# Wait for user input in DM
		def check(m):
			return m.author.id == user.id and m.channel.id == dm_channel.id
		
		try:
			user_message = await ctx.bot.wait_for('message', timeout=120.0, check=check)
		except asyncio.TimeoutError:
			await dm_channel.send("Temps écoulé. Opération annulée.")
		else:
			new_value = user_message.content
			trema_db.set_server_welcome_msg(guild_id, new_value)
			embed_title = "Message d'accueil mis à jour"
			response_embed = _make_config_confirm_embed(
				embed_title, new_value, prev_value)
			await dm_channel.send(embed=response_embed)

	@config.command(name="msgdepart",
		description=f"{_MEMBER_MENTIONABLE} Changer le message affiché lorsqu'un membre quitte le serveur")
	@is_authorized(trema_db)
	async def config_leave_msg(ctx,
			message: Option(str, f"{_MEMBER_MENTIONABLE} Nouveau message de départ.")):
		
		guild_id = ctx.guild_id
		embed_title = _make_cmd_full_name(ctx.command) + _SPACE + message
		prev_value = trema_db.get_server_leave_msg(guild_id)

		if message == _REQUEST_VALUE:
			response_embed =\
				_make_config_display_embed(embed_title, prev_value)

		else:
			trema_db.set_server_leave_msg(guild_id, message)
			confirmed_msg = trema_db.get_server_leave_msg(guild_id)
			response_embed = _make_config_confirm_embed(
				embed_title, confirmed_msg, prev_value)

		await ctx.respond(embed=response_embed, ephemeral=True)

	return config

def _create_config_reminder_cmds(trema_db, config_group):
	rappel = config_group.create_subgroup("rappel",
		description="Configurez le rappel aux membres qui n'ont pas choisi de rôles.")

	@rappel.command(name="message",
		description=f"{_MEMBER_MENTIONABLE} Changez le message de rappel aux membres sans rôles.")
	@is_authorized(trema_db)
	async def config_reminder_msg(ctx,
			message: Option(str, f"{_MEMBER_MENTIONABLE} Message de rappel aux membres sans rôles.")):
		
		guild_id = ctx.guild_id
		embed_title = _make_cmd_full_name(ctx.command) + _SPACE + message
		prev_value = trema_db.get_server_reminder_msg(guild_id)

		if message == _REQUEST_VALUE:
			response_embed =\
				_make_config_display_embed(embed_title, prev_value)

		else:
			trema_db.set_server_reminder_msg(guild_id, message)
			confirmed_msg = trema_db.get_server_reminder_msg(guild_id)
			response_embed = _make_config_confirm_embed(
				embed_title, confirmed_msg, prev_value)

		await ctx.respond(embed=response_embed, ephemeral=True)

	@rappel.command(name="delai",
		description="Changer le délai d'envoi du rappel (minutes) aux membres sans rôles.")
	@is_authorized(trema_db)
	async def config_reminder_delay(ctx,
			delai: Option(str, "Délai du rappel (minutes) aux membres sans rôles")):
		
		guild_id = ctx.guild_id
		embed_title = _make_cmd_full_name(ctx.command) + _SPACE + delai
		prev_value = trema_db.get_server_reminder_delay(guild_id) / 60
		prev_value = int(prev_value)

		try:
			delai = int(delai) * 60

		except ValueError:
			pass

		if isinstance(delai, str) and delai == _REQUEST_VALUE:
				response_embed = _make_config_display_embed(embed_title, prev_value)
			
		elif not isinstance(delai, int) or delai < 0:
			response_embed = _make_config_error_embed(embed_title, prev_value,
				"Le délai de rappel (minutes) est un nombre entier positif.")

		else:
			trema_db.set_server_reminder_delay(guild_id, delai)
			confirmed_delay = trema_db.get_server_reminder_delay(guild_id) / 60
			confirmed_delay = int(confirmed_delay)
			response_embed = _make_config_confirm_embed(
				embed_title, confirmed_delay, prev_value)

		await ctx.respond(embed=response_embed, ephemeral=True)

def _create_information_cmds(trema_bot, start_time):	
	@trema_bot.command(name="ping", description="Répond avec pong")
	async def ping(ctx):
		latency = round(trema_bot.latency * 1000) 
		uptime = datetime.now() - start_time
		uptime_str = str(uptime).split('.')[0]  # remove the microseconds part
		server_count = len(trema_bot.guilds)

		response_embed = Embed(
			title="Pong!",
			color=Color.green()
		)
		response_embed.add_field(name="Latency", value=f"{latency}ms")
		response_embed.add_field(name="Uptime", value=uptime_str)
		response_embed.add_field(name=f'{trema_bot.user} server Count', value=str(server_count))

		await ctx.respond(embed=response_embed)


	@trema_bot.command(name="info", description="Informations sur Trëma")
	async def info(ctx):
		embed_title = _make_cmd_full_name(ctx.command)
		instructions =\
			"Trëma est un bot Discord dedié à accueillir et guider les membres du serveur.\n\n"\
			+ "Trëma est développé par le club CEDILLE de l'ÉTS."
		
		help_embed = Embed(
			title=embed_title,
			description=instructions,
			color=Color.blue())
		help_embed.set_thumbnail(url="https://cedille.etsmtl.ca/images/cedille-logo-orange.png")
			
		await ctx.respond(embed=help_embed)

def _create_management_cmds(trema_bot, trema_db):

	@trema_bot.command(name="annonce", description="Informations sur Trëma")
	@is_authorized(trema_db)
	async def annonce(ctx):

		await ctx.respond("Veuillez vérifier vos messages privés pour des instructions supplémentaires.", ephemeral=True)

		mention_dict = generate_mention_dict(ctx.guild)
		
		time_and_date, delay = await prompt_user_with_date(ctx, "Quelle est la date et l'heure de l'annonce ? (AAAA-MM-JJ HH:MM:SS)", 'Date et heure')
		if not time_and_date:
			return

		title = await prompt_user(ctx, "Quel est le titre de l\'annonce ?", 'Titre')
		if not title:
			return

		body = await prompt_user(ctx, "Entrez le corps de l\'annonce:" 
			   						"\nPour personnaliser ce message, vous pouvez utiliser les mentions suivantes:\n"
									"- `{username}` pour mentionner un username\n"
									"- `{server}` pour le nom du serveur\n"
									"- `{&role}` pour mentionner un rôle par son nom\n"
									"- `{#channel}` pour un lien vers un canal\n"
									"- `{everyone}` pour `@everyone`\n"
									"- `{here}` pour `@here`\n\n", 'Contenu de l\'annonce')
		if not body:
			return

		try_again_msg = True
		while True:
			try:
				channel_name = await prompt_user(ctx, 'Entrer le canal pour afficher l\'annonce : ', 'Choisir canal')
				if not channel_name:
					return
				channel = utils.get(ctx.guild.text_channels, name=channel_name)
				
				if channel is not None:
					confirm_msg = await prompt_user_with_confirmation(ctx, f"Canal :`{channel}`. Confirmez-vous le canal trouvé ?", 'Choisir canal')
					
					if confirm_msg :
						break
				else:
					try_again_msg = await prompt_user_with_confirmation(ctx, "Canal non trouvé. Voulez-vous essayer à nouveau ?", 'Choisir canal')
					
					if not try_again_msg:
						await ctx.author.send("Operation annulé.")
						break

			except asyncio.TimeoutError:
				await ctx.author.send("Temps écoulé. Opération annulée.")
				break
		
		# User canceled the operation
		if not try_again_msg:
			return

		is_embed = await prompt_user_with_confirmation(ctx, "Voulez-vous que l'annonce soit intégrée (embedded)?")
		image_path = None
		if is_embed == True:
			image_url = await prompt_user(ctx, 'Entrez l\'URL de l\'image à intégrer (ou tapez \'aucun\'):',  'Image à intégrer')
			if not image_url:
				return
		elif is_embed == False:
			image_path = await prompt_for_image(ctx)
		else :
			return

		body_with_mentions = make_mention(body, mention_dict)

		confirmation = Embed(title="Détails de l'annonce", description=f"Date de l'annonce : {time_and_date}\nCanal pour l'annonce : {channel}\n\nAperçu de l'annonce dans le prochain message :", color=Color.blurple())
		await ctx.author.send(embed=confirmation)	

		if is_embed: 
			annonce = Embed(title=title, description=body_with_mentions, color=Color.blurple())
			if image_url.lower() != 'aucun':
				annonce.set_thumbnail(url=image_url)
			await ctx.author.send(embed=annonce)
		else:
			formatted_title = f"**{title}**\n"
			formatted_body = f"{body_with_mentions}"
			annonce = f"{formatted_title}\n{formatted_body}"
			await ctx.author.send(annonce)
			if image_path:
				file = File(image_path, filename=image_path.split("/")[-1])
				await ctx.author.send(file=file)

		final_confirmation = await prompt_user_with_confirmation(ctx, "Confirmez-vous ces détails ?")
	
		if final_confirmation:
			condition = lambda: True 
			asyncio.create_task(send_delayed_dm(channel, annonce, delay, condition, 'embed' if is_embed else 'text'))
			if image_path:
				file = File(image_path, filename=image_path.split("/")[-1])
				asyncio.create_task(send_delayed_dm(channel, file, delay, condition, 'file', image_path))
			await ctx.author.send('Annonce programmée.')
		else:
			await ctx.author.send('Annonce annulée.')

def _create_webhooks_cmds(trema_db):
	webhook = SlashCommandGroup(name="webhook",
		description="Groupe de commandes pour gérer les webhooks.")

	@webhook.command(name="create",
		description="Créer un webhook pour le canal spécifié")
	@is_authorized(trema_db)
	async def create_webhook(ctx,
			channel_id: Option(str, "Le canal affilié au webhook qui sera créé"),
			webhook_name: Option(str, "Le nom du webhook qui sera créé")):
		
		guild_id = ctx.guild_id
		unique_url = generate_unique_webhook_url()

		# Save the unique URL and associated channel to your database
		trema_db.create_webhook(webhook_name, channel_id, unique_url, guild_id)

		embed=Embed(title="Webhook créé", description=f"Le webhook '{webhook_name}' a été créé avec succès.\n```webhook url endpoint : {unique_url}```", color=Color.blurple())
		await ctx.respond(embed=embed, ephemeral=True)

	@webhook.command(name="list",
		description="Liste des webhooks existants")
	@is_authorized(trema_db)
	async def list_webhooks(ctx):
		webhooks = trema_db.get_all_webhooks(ctx.guild.id)
		if webhooks == []:
			embed=Embed(title="Liste des webhooks", description=f"Aucun webhook n'existe pour ce serveur.", color=Color.blurple())
			await ctx.respond(embed=embed, ephemeral=True)
			return
		
		webhook_strings = []
		for webhook in webhooks:
			webhook_str = f"Name: {webhook.get('webhookName', 'Unknown')}, Channel ID: {webhook.get('channelID', 'Unknown')}"
			webhook_strings.append(webhook_str)
			
		embed=Embed(title="Liste des webhooks", description=f"Voici la liste des webhooks existants :\n" + f'\n'.join(webhook_strings), color=Color.blurple())
		await ctx.respond(embed=embed, ephemeral=True)

	@webhook.command(name="delete",
		description="Supprime le webhook référencé")
	@is_authorized(trema_db)
	async def delete_webhook(ctx, webhook_name: Option(str, "Le nom du webhook à supprimer")):
		# Your logic here to delete the specified webhook
		webhook = trema_db.get_webhook_by_name(webhook_name, ctx.guild.id)
		if webhook is None:
			embed=Embed(title="Webhook non trouvé", description=f"Le webhook '{webhook_name}' n'existe pas.", color=Color.blurple())
			await ctx.respond(embed=embed, ephemeral=True)
			return
		
		trema_db.delete_webhook(webhook_name, ctx.guild.id)

		embed_title = _make_cmd_full_name(ctx.command) + _SPACE + webhook_name
		embed = Embed(title=embed_title, description=f"Webhook '{webhook_name}' supprimé.", color=Color.blurple())
		await ctx.respond(embed=embed, ephemeral=True)
    
	@webhook.command(name="update",
		description="Met à jour le canal lié au webhook")
	@is_authorized(trema_db)
	async def update_webhook(ctx,
			webhook_name: Option(str, "Le nom du webhook à mettre à jour"),
			new_channel_id: Option(str, "Le nouveau canal à associer au webhook")):

		new_channel = ctx.guild.get_channel(int(new_channel_id))
		if new_channel:
			trema_db.update_webhook_channel(webhook_name, new_channel.id, ctx.guild.id)
			embed=Embed(title="Webhook mis à jour", description=f"Le webhook '{webhook_name}' a été mis à jour pour le canal {new_channel_id} avec succès.", color=Color.blurple())
			await ctx.respond(embed=embed, ephemeral=True)
		else:
			await ctx.respond(f"Le canal '{new_channel_id}' n'existe pas.", ephemeral=True)

	return webhook