"""
Trëma est un robot logiciel pour le serveur
Discord des clubs étudiants de l'ÉTS.
"""


from argparse import ArgumentParser
import discord


def _make_arg_parser():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("-s", "--serveurs", nargs="+", type=str,
		help="L'identifiant des serveurs où ce robot fonctionnera")
	parser.add_argument("-j", "--jeton", type=str,
		help="Le jeton d'authentification de ce robot logiciel")
	return parser


arg_parser = _make_arg_parser()
args = arg_parser.parse_args()

server_ids = args.serveurs
bot_token = args.jeton

intents = discord.Intents.default()
intents.members = True

trema = discord.Bot(intents=intents)


@trema.slash_command(guild_ids=server_ids, name="hello")
async def hello(ctx):
    await ctx.respond("Hello!")


@trema.event
async def on_member_join(member):
	guild = member.guild
	sys_chan = guild.system_channel
	welcome_msg = "Bonjour"
#	welcome_msg =\
#		f"Heille {member.mention}!" +\
#		f"\nBienvenue au Club CEDILLE. Rends-toi dans {sys_chan.name}" +\
#		"pour avoir accès au reste du serveur!"
	await sys_chan.send(welcome_msg)


@trema.event
async def on_member_remove(member):
	guild = member.guild
	sys_chan = guild.system_channel
	message = f"{member.name} décâlisse."
	await sys_chan.send(message)


@trema.event
async def on_ready():
    print(f"{trema.user} fonctionne.")


trema.run(bot_token)
