from discord import\
	Color,\
	Embed,\
	Option,\
	SlashCommandGroup
from cogs.utils.text_format import\
	_SPACE,\
	_REQUEST_VALUE,\
	_MEMBER_MENTIONABLE,\
	_make_cmd_full_name,\
	_make_config_confirm_embed,\
	_make_config_error_embed,\
	_make_config_display_embed
from cogs.admin import is_authorized
from cogs.utils.discord import get_channel_name
from cogs.config.rappel import _create_config_reminder_cmds
import asyncio

def _create_config_cmds(trema_db):
	config = SlashCommandGroup(name="config",
		description="Configurez les options de Trëma pour votre serveur.")
	
	_create_config_reminder_cmds(trema_db, config)

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
	
	@config.command(name="memberrole",
		description="Configurer le rôle des membres approuvés.")
	@is_authorized(trema_db)
	async def config_member_role(ctx, 
			role_id: Option(str, "L'ID du rôle des membres approuvés.")):
		
		try:
			role_id = int(role_id)
		except ValueError:
			await ctx.respond("Rôle invalide. Veuillez vérifier l'ID du rôle.", ephemeral=True)
			return
		
		server_id = ctx.guild.id
		role = ctx.guild.get_role(role_id)

		if not role:
			await ctx.respond("Rôle invalide. Veuillez vérifier l'ID du rôle.", ephemeral=True)
			return

		trema_db.set_server_member_role(server_id, role_id)

		await ctx.respond(f"Le rôle des membres approuvés a été configuré avec succès : {role.name} (ID: {role_id}).", ephemeral=True)


	@config.command(name="enablecalidum",
		description="Activer ou désactiver les notifications Calidum.")
	@is_authorized(trema_db)
	async def config_calidum(ctx,
			enable: Option(bool, "Activer ou désactiver les notifications Calidum")):
		
		server_id = ctx.guild.id
		prev_value = trema_db.get_server_calidum_enabled(server_id)
		embed_title = _make_cmd_full_name(ctx.command) + _SPACE + str(enable)

		if enable == _REQUEST_VALUE:
			response_embed = _make_config_display_embed(embed_title, prev_value)

		else:
			trema_db.set_server_calidum_enabled(server_id, enable)
			confirmed_value = trema_db.get_server_calidum_enabled(server_id)
			response_embed = _make_config_confirm_embed(
				embed_title, confirmed_value, prev_value)

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
			+ "Certains paramètres sont des messages affichés après un évènement concernant "\
			+ "un membre particulier. Pour mentionner ce membre, écrivez **@-** dans ces messages. "\
			+ "Le signe **[@-]** au début d'une description indique que cette action est possible." 
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
			response_embed = _make_config_confirm_embed(embed_title, new_value, prev_value)
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

	@config.command(name="server_roles", description="Configurer les rôles d'accès au serveur.")
	@is_authorized(trema_db)
	async def config_server_roles(ctx, roles: Option(str, "Entrez les noms des rôles séparés par une virgule.")):
		role_names = [role.strip() for role in roles.split(",")]
		server_id = ctx.guild.id
		trema_db.set_server_roles(server_id, role_names)

		await ctx.respond(f"Les rôles du serveur ont été configurés avec succès : {', '.join(role_names)}.", ephemeral=True)


	@config.command(name="set_request_join_msg", description="Configurer le message de bienvenue pour la commande /request join.")
	@is_authorized(trema_db)
	async def config_member_join_msg(ctx):
		guild_id = ctx.guild.id
		
		prev_value = trema_db.get_server_member_join_msg(guild_id)

		await ctx.respond("Veuillez vérifier vos messages privés pour des instructions supplémentaires.", ephemeral=True)

		user = ctx.author
		dm_channel = user.dm_channel
		if dm_channel is None:
			dm_channel = await user.create_dm()

		embed = Embed(
			title="Configuration du message de bienvenue",
			description=f"Le message de bienvenue actuel est: `{prev_value}`\n\n"
						"Vous pouvez personnaliser ce message qui permet \n"
						"d'indiquer à l'utilisateur les rôles qui s'offre a \n"
						"celui-ci pour accéder au reste du serveur.",
			color=Color.blue()
		)

		await dm_channel.send(embed=embed)

		def check(m):
			return m.author.id == user.id and m.channel.id == dm_channel.id

		try:
			user_message = await ctx.bot.wait_for('message', timeout=120.0, check=check)
		except asyncio.TimeoutError:
			await dm_channel.send("Temps écoulé. Opération annulée.")
		else:
			new_value = user_message.content
			trema_db.set_server_member_join_msg(guild_id, new_value)
			confirmed_msg = trema_db.get_server_member_join_msg(guild_id)
			
			embed_title = "Message pour les requêtes de membre mis à jour"
			response_embed = _make_config_confirm_embed(embed_title, confirmed_msg, prev_value)
			
			await dm_channel.send(embed=response_embed)

	return config
