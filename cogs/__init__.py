from cogs.members import _create_member_cmds
from cogs.ctf import _create_odyssee_cmds
from cogs.config import _create_config_cmds
from cogs.information import _create_information_cmds
from cogs.admin.management import _create_server_management_cmds
from cogs.webhooks import _create_webhooks_cmds
from cogs.requests import _create_requests_cmds

def create_slash_cmds(trema_bot, trema_db, start_time, github_token):
	_create_information_cmds(trema_bot, start_time, trema_db)
	_create_server_management_cmds(trema_bot, trema_db)
	_create_odyssee_cmds(trema_bot)
	
	config = _create_config_cmds(trema_db)
	webhook = _create_webhooks_cmds(trema_db)
	request = _create_requests_cmds(trema_db, github_token)
	member 	= _create_member_cmds(trema_db, github_token)
	
	trema_bot.add_application_command(config)
	trema_bot.add_application_command(webhook)
	trema_bot.add_application_command(request)
	trema_bot.add_application_command(member)
