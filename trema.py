"""
Trëma est un robot logiciel pour le serveur
Discord des clubs étudiants de l'ÉTS.
"""


from argparse import ArgumentParser
import asyncio
import discord

from pymongo import MongoClient

from discord_util import\
	get_channel_by_name,\
	member_roles_are_default,\
	send_delayed_dm


client = MongoClient("mongodb://root:root@localhost:27017/?authSource=admin")
#database Trema
mydb = client["trema"]
#table serveur contenant les différents serveur utiliser par trema
mycol = mydb["serveur"]

###############
# À enlever : 
# Exemple de comment l'utiliser : 
mydict = { "name": "cedille", "members_count": 85 }
record = mycol.insert_one(mydict)

# Équivalent à SELECT *
for i in mycol.find():
  print(i)


mycol.drop()
###############

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
print(type(trema))


@trema.event
async def on_member_join(member):
	guild = member.guild
	sys_chan = guild.system_channel
	# A channel that contains integration instructions
	instruct_chan = get_channel_by_name(trema, "accueil")
	welcome_msg =\
		f"Heille {member.mention}!"\
		+ f"\nBienvenue au Club CEDILLE. "\
		+ f"Suis les instructions dans {instruct_chan.mention} "\
		+ "pour avoir accès au reste du serveur!"
	await sys_chan.send(welcome_msg)

	# A reminder if the new member does not select a role
	if not member.bot:
		reminder_msg =\
			f"Viens dans {instruct_chan.mention} pour t'attribuer un rôle!"
		msg_condition = lambda: member_roles_are_default(member)
		reminder_task = asyncio.create_task(send_delayed_dm(
			member, reminder_msg, _DELAY_SECS_15_MIN, msg_condition))
		await asyncio.wait([reminder_task])


@trema.event
async def on_member_remove(member):
	guild = member.guild
	sys_chan = guild.system_channel
	message = f"{member.name} a quitté le serveur."
	await sys_chan.send(message)


@trema.event
async def on_ready():
    print(f"{trema.user} fonctionne.")


trema.run(bot_token)
