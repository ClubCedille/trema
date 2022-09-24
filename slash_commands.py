from discord import Option


_ARG_CANAL_ACCUEIL = "canalaccueil"
_ARG_MSG_ACCUEIL = "msgaccueil"

_CONFIG_DESC = "Configurez les options de Trëma pour votre serveur.\n"\
	+ _ARG_CANAL_ACCUEIL + " (int): l'identifiant du canal où les nouveaux membres reçoivent un message à leur arrivée.\n"\
	+ _ARG_MSG_ACCUEIL + " (str): le message d'acceuil pour les nouveaux membres"


def create_slash_cmds(trema_bot, trema_db, server_id):
	server_ids = (server_id,)

	@trema_bot.slash_command(guild_ids=server_ids,
		name="config", describe=_CONFIG_DESC)
	async def config(ctx, option: Option(str), value: Option):

		if option == _ARG_CANAL_ACCUEIL:
			trema_db.set_server_welcome_chan_id(server_id, value)

		elif option == _ARG_MSG_ACCUEIL:
			trema_db.set_server_welcome_msg(server_id, value)
