from discord import\
	Color,\
	Embed,\
	Option

from discord_util import\
	get_channel_name


_ARG_CANAL_ACCUEIL = "canalaccueil"
_ARG_MSG_ACCUEIL = "msgaccueil"
_ARG_MSG_DEPART	 = "msgdepart"

_CONFIG_DESC = "Configurez les options de Trëma pour votre serveur."


def create_slash_cmds(trema_bot, trema_db, server_ids):
	@trema_bot.slash_command(guild_ids=server_ids,
		name="config", description=_CONFIG_DESC)
	async def config(ctx,
			param: Option(str, "Paramètre à régler"),
			value: Option(str, "Valeur du paramètre")):
		await _slash_cmd_config(ctx, trema_db, param, value)


async def _slash_cmd_config(ctx, trema_db, param, value):
	guild = ctx.guild
	guild_id = ctx.guild_id
	embed_title = "Paramètre mis à jour: "

	if param == _ARG_CANAL_ACCUEIL:
		welcome_chan_id = int(value)
		embed_title += "canal d'accueil"

		prev_value = trema_db.get_server_welcome_chan_id(guild_id)
		welcome_chan_name = get_channel_name(guild, prev_value)
		prev_value = f"{welcome_chan_name} ({prev_value})"

		welcome_chan_name = get_channel_name(guild, welcome_chan_id)
		updated_value = f"{welcome_chan_name} ({welcome_chan_id})"

		trema_db.set_server_welcome_chan_id(guild_id, welcome_chan_id)

	elif param == _ARG_MSG_ACCUEIL:
		embed_title += "message d'accueil"
		prev_value = trema_db.get_server_welcome_msg(guild_id)
		updated_value = value
		trema_db.set_server_welcome_msg(guild_id, value)

	elif param == _ARG_MSG_DEPART:
		embed_title += "message de départ"
		prev_value = trema_db.get_server_leave_msg(guild_id)
		updated_value = value
		trema_db.set_server_leave_msg(guild_id, value)

	else:
		return

	confirm_embed = Embed(
		title=embed_title,
		description=f"Nouvelle valeur: {updated_value}\nValeur précédente: {prev_value}",
		color=Color.green())

	await ctx.send(embed=confirm_embed)
