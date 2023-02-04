"""
Trëma est un robot logiciel pour le serveur
Discord des clubs étudiants de l'ÉTS.
"""

import os
import discord
import sys

from events import\
	create_event_reactions

from slash_commands import\
	create_slash_cmds

from trema_database import\
	get_trema_database

bot_token = os.getenv('DISCORD_TOKEN')
if not bot_token:
    print('ERROR: Token var is missing: DISCORD_TOKEN')
    sys.exit(-1)

intents = discord.Intents.default()

trema = discord.Bot(intents=intents)

database = get_trema_database()

create_event_reactions(trema, database)
create_slash_cmds(trema, database)

trema.run(bot_token)
