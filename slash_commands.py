import asyncio
from discord import\
	Color,\
	Embed,\
	Option,\
	SlashCommandGroup,\
	File

from discord_util import\
	get_channel_name

from datetime import datetime

_MEMBER_MENTIONABLE = "[@-]"
_REQUEST_VALUE = "$"
_SLASH = "/"
_SPACE = " "


def create_slash_cmds(trema_bot, trema_db, start_time):
	config = _create_config_cmds(trema_db)
	_create_config_reminder_cmds(trema_db, config)
	_create_information_cmds(trema_bot, start_time)
	trema_bot.add_application_command(config)


def _create_config_cmds(trema_db):
	config = SlashCommandGroup(name="config",
		description="Configurez les options de Trëma pour votre serveur.")

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
						"- `{channel}` pour le nom du canal\n"
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
			user_message = await ctx.bot.wait_for('message', timeout=60.0, check=check)
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
		response_embed.add_field(name="Trëma server Count", value=str(server_count))

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

def _make_cmd_full_name(cmd):
	names = list()

	while cmd is not None:
		names.insert(0, cmd.name)
		cmd = cmd.parent

	full_name = _SLASH + _SPACE.join(names)

	return full_name


def _make_config_confirm_embed(title, updated_value, prev_value):
	confirm_embed = Embed(
		title=title,
		description=f"Nouvelle valeur:\n`{updated_value}`\n\nValeur précédente:\n`{prev_value}`",
		color=Color.green())
	return confirm_embed


def _make_config_display_embed(title, current_value):
	display_embed = Embed(
		title=title,
		description=f"Valeur actuelle: {current_value}",
		color=Color.green())
	return display_embed


def _make_config_error_embed(title, current_value, error_msg):
	error_embed = Embed(
		title=title,
		description=
			f"ERREUR!\n{error_msg}\n\nValeur actuelle: {current_value}",
		color=Color.red())
	return error_embed
