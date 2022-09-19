"""
Trëma est un robot logiciel pour le serveur
Discord des clubs étudiants de l'ÉTS.
"""


from argparse import ArgumentParser
import asyncio
import discord

from discord_util import\
	get_channel_by_name,\
	member_roles_are_default,\
	send_delayed_dm

from trema_database import\
	get_trema_database


_DELAY_SECS_15_MIN = 15 * 60


def _make_arg_parser():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("-s", "--serveur", type=str,
		help="L'identifiant du serveur où ce robot fonctionnera")
	parser.add_argument("-j", "--jeton", type=str,
		help="Le jeton d'authentification de ce robot logiciel")
	return parser


arg_parser = _make_arg_parser()
args = arg_parser.parse_args()

server_ids = (args.serveur,)
bot_token = args.jeton

intents = discord.Intents.default()
intents.members = True

trema = discord.Bot(intents=intents)

database = get_trema_database()


@trema.event
async def on_member_join(member):
	guild = member.guild
	sys_chan = guild.system_channel
	# A channel that contains integration instructions
	#instruct_chan = get_channel_by_name(trema, "accueil")

	welcome_id = database.get_server_info(guild.id)["welcome_id"]
	welcome_info = database.get_welcome_info(welcome_id)
	welcome_msg = welcome_info["welcome_msg"]
	#welcome_msg =\
	#	f"Heille {member.mention}!"\
	#	+ f"\nBienvenue au Club CEDILLE. "\
	#	+ f"Suis les instructions dans {instruct_chan.mention} "\
	#	+ "pour avoir accès au reste du serveur!"
	await sys_chan.send(welcome_msg)

	# A reminder if the new member does not select a role
	if not member.bot:
		reminder_msg = welcome_info["reminder_msg"]
		#reminder_msg =\
		#	f"Viens dans {instruct_chan.mention} pour t'attribuer un rôle!"
		msg_condition = lambda: member_roles_are_default(member)
		reminder_task = asyncio.create_task(send_delayed_dm(
			member, reminder_msg, _DELAY_SECS_15_MIN, msg_condition))
		await asyncio.wait([reminder_task])


@trema.event
async def on_member_remove(member):
	guild = member.guild
	sys_chan = guild.system_channel
	welcome_id = database.get_server_info(guild.id)["welcome_id"]
	welcome_info = database.get_welcome_info(welcome_id)
	leave_msg = welcome_info["leave_msg"]
	#leave_msg = f"{member.name} a quitté le serveur."
	await sys_chan.send(leave_msg)


@trema.event
async def on_ready():
    print(f"{trema.user} fonctionne.")


trema.run(bot_token)
