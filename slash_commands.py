from discord import\
	Color,\
	Embed,\
	Option,\
	SlashCommandGroup

from discord_util import\
	get_channel_name


_MEMBER_MENTION  = "«@-»"

_SLASH = "/"
_SPACE = " "

_REQUEST_VALUE = "$"


def create_slash_cmds(trema_bot, trema_db):
	config = SlashCommandGroup(name="config",
		description="Configurez les options de Trëma pour votre serveur.")

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

		await ctx.send(embed=response_embed)

	@config.command(name="msgaccueil",
		description="Changer le message affiché lorsqu'un membre arrive dans le serveur")
	async def config_welcome_msg(ctx,
			message: Option(str, f"Nouveau message d'accueil. {_MEMBER_MENTION} pour mentionner le nouveau membre.")):
		guild_id = ctx.guild_id
		embed_title = _make_cmd_full_name(ctx.command) + _SPACE + message
		prev_value = trema_db.get_server_welcome_msg(guild_id)

		if message == _REQUEST_VALUE:
			response_embed =\
				_make_config_display_embed(embed_title, prev_value)

		else:
			trema_db.set_server_welcome_msg(guild_id, message)
			confirmed_msg = trema_db.get_server_welcome_msg(guild_id)
			response_embed = _make_config_confirm_embed(
				embed_title, confirmed_msg, prev_value)

		await ctx.send(embed=response_embed)

	@config.command(name="msgdepart",
		description="Changer le message affiché lorsqu'un membre quitte le serveur")
	async def config_leave_msg(ctx,
			message: Option(str, f"Nouveau message de départ. {_MEMBER_MENTION} pour mentionner le membre qui part.")):
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

		await ctx.send(embed=response_embed)

	rappel = config.create_subgroup("rappel",
		description="Configurez le rappel aux membres qui n'ont pas choisi de rôles.")

	@rappel.command(name="message",
		description="Changez le message de rappel aux membres sans rôles.")
	async def config_reminder_msg(ctx,
			message: Option(str, f"Message de rappel aux membres sans rôles. {_MEMBER_MENTION} pour mentionner le membre.")):
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

		await ctx.send(embed=response_embed)

	@rappel.command(name="delai",
		description="Changer le délai d'envoi du rappel aux membres sans rôles (minutes).")
	async def config_reminder_delay(ctx,
			delay: Option(str, "Délai du rappel aux membres sans rôles")):
		guild_id = ctx.guild_id
		embed_title = _make_cmd_full_name(ctx.command) + _SPACE + delay
		prev_value = trema_db.get_server_reminder_delay(guild_id)

		try:
			delay = int(delay) * 60

		except ValueError:
			pass

		if isinstance(delay, str) and delay == _REQUEST_VALUE:
				response_embed = _make_config_display_embed(embed_title, prev_value)
			
		elif not isinstance(delay, int) or delay < 0:
			response_embed = _make_config_error_embed(embed_title, prev_value,
				"Le délai de rappel (minutes) est un nombre entier positif.")

		else:
			trema_db.set_server_reminder_delay(guild_id, delay)
			confirmed_delay = trema_db.get_server_reminder_delay(guild_id)
			response_embed = _make_config_confirm_embed(
				embed_title, confirmed_delay, prev_value)

		await ctx.send(embed=response_embed)

	trema_bot.add_application_command(config)


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
		description=f"Nouvelle valeur: {updated_value}\nValeur précédente: {prev_value}",
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
