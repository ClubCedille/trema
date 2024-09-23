from discord import Embed, Color, SlashCommandGroup, Option
from cogs.admin import is_authorized
from cogs.utils.dispatch import dispatch_github_workflow, post_to_calidum
from cogs.requests.join import _create_member_requests_cmds
from cogs.requests.grav import _create_grav_requests_cmds

def _create_requests_cmds(trema_db, github_token):
	request = SlashCommandGroup(name="request",
		description="Groupe de commandes pour gérer les requêtes.")
	
	_create_member_requests_cmds(trema_db, request)
	_create_grav_requests_cmds(trema_db, request, github_token)

	return request