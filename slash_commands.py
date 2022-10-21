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
		id_accueil = int(id_accueil)

		guild = ctx.guild
		guild_id = ctx.guild_id
		embed_title = "Paramètre mis à jour: canal d'accueil"

		prev_value = trema_db.get_server_welcome_chan_id(guild_id)
		welcome_chan_name = get_channel_name(guild, prev_value)
		prev_value = f"{welcome_chan_name} ({prev_value})"

		welcome_chan_name = get_channel_name(guild, id_accueil)
		updated_value = f"{welcome_chan_name} ({id_accueil})"

		trema_db.set_server_welcome_chan_id(guild_id, id_accueil)

		confirm_embed = _make_config_confirm_embed(
			embed_title, updated_value, prev_value)

		await ctx.send(embed=confirm_embed)

	@config.command(name="msgaccueil",
			desciption="Changer le message d'accueil des nouveaux membres")
	async def config_welcome_msg(ctx, message: Option(str, "Nouveau message d'accueil")):
		guild_id = ctx.guild_id
		embed_title = "Paramètre mis à jour: message d'accueil"

		prev_value = trema_db.get_server_welcome_msg(guild_id)
		updated_value = message
		trema_db.set_server_welcome_msg(guild_id, message)

		confirm_embed = _make_config_confirm_embed(
			embed_title, updated_value, prev_value)

		await ctx.send(embed=confirm_embed)

	trema_bot.add_application_command(config)


def _make_config_confirm_embed(title, updated_value, prev_value):
	confirm_embed = Embed(
	title=title,
	description=f"Nouvelle valeur: {updated_value}\nValeur précédente: {prev_value}",
	color=Color.green())
	return confirm_embed
