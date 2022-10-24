from discord import\
	Color,\
	Embed,\
	Option,\
	SlashCommandGroup

from discord_util import\
	get_channel_name


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
		embed_title = _make_cmd_full_name(ctx.command)

		prev_value = trema_db.get_server_welcome_chan_id(guild_id)
		welcome_chan_name = get_channel_name(guild, prev_value)
		prev_value = f"{welcome_chan_name} ({prev_value})"

		try:
			# The command argument is a string.
			id_accueil = int(id_accueil)
			welcome_chan_name = get_channel_name(guild, id_accueil)

		except ValueError:
			pass

		if not isinstance(id_accueil, int) or id_accueil < 0:
			error_msg_base =\
				"L'identifiant des canaux est un nombre entier positif.\n"\
				+ "Argument reçu: "
			response_embed = _make_config_error_embed(embed_title, prev_value,
				error_msg_base + str(id_accueil))

		elif welcome_chan_name is None:
			response_embed = _make_config_error_embed(embed_title, prev_value,
				f"{guild.name} n'a pas de canal {id_accueil}.")

		else:
			updated_value = f"{welcome_chan_name} ({id_accueil})"

			trema_db.set_server_welcome_chan_id(guild_id, id_accueil)

			response_embed = _make_config_confirm_embed(
				embed_title, updated_value, prev_value)

		await ctx.send(embed=response_embed)

	@config.command(name="msgaccueil",
			desciption="Changer le message d'accueil des nouveaux membres")
	async def config_welcome_msg(ctx, message: Option(str, "Nouveau message d'accueil")):
		guild_id = ctx.guild_id
		embed_title = _make_cmd_full_name(ctx.command)

		prev_value = trema_db.get_server_welcome_msg(guild_id)
		trema_db.set_server_welcome_msg(guild_id, message)

		confirm_embed = _make_config_confirm_embed(
			embed_title, message, prev_value)

		await ctx.send(embed=confirm_embed)

	@config.command(name="msgdepart",
		description="Changer le message affiché lorsqu'un membre quitte le serveur")
	async def config_leave_msg(ctx, message: Option(str, "Nouveau message de départ")):
		guild_id = ctx.guild_id
		embed_title = _make_cmd_full_name(ctx.command)

		prev_value = trema_db.get_server_leave_msg(guild_id)
		trema_db.set_server_leave_msg(guild_id, message)

		confirm_embed = _make_config_confirm_embed(
			embed_title, message, prev_value)

		await ctx.send(embed=confirm_embed)

	trema_bot.add_application_command(config)


def _make_cmd_full_name(cmd):
	names = list()

	while cmd is not None:
		names.insert(0, cmd.name)
		cmd = cmd.parent

	full_name = "/" + " ".join(names)

	return full_name


def _make_config_confirm_embed(title, updated_value, prev_value):
	confirm_embed = Embed(
		title=title,
		description=f"Nouvelle valeur: {updated_value}\nValeur précédente: {prev_value}",
		color=Color.green())
	return confirm_embed


def _make_config_error_embed(title, current_value, error_msg):
	error_embed = Embed(
		title=title,
		description=f"ERREUR!\n{error_msg}\n\nParamètre actuel: {current_value}",
		color=Color.red())
	return error_embed
