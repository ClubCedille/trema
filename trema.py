"""
Trëma est un robot logiciel pour le serveur
Discord des clubs étudiants de l'ÉTS.
"""


from argparse import ArgumentParser
import discord

from events import\
	create_event_reactions

from slash_commands import\
	create_slash_cmds

from trema_database import\
	get_trema_database


def _make_arg_parser():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("-j", "--jeton", type=str,
		help="Le jeton d'authentification de ce robot logiciel")
	return parser


arg_parser = _make_arg_parser()
args = arg_parser.parse_args()

bot_token = args.jeton

intents = discord.Intents.default()
intents.members = True

trema = discord.Bot(intents=intents)

database = get_trema_database()

create_event_reactions(trema, database)
create_slash_cmds(trema, database)

trema.run(bot_token)
