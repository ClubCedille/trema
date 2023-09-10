"""
Trëma est un robot logiciel pour le serveur
Discord des clubs étudiants de l'ÉTS.
"""
import os
import discord
import sys
from datetime import datetime
from quart import Quart
import asyncio
from events import\
	create_event_reactions
from slash_commands import\
	create_slash_cmds
from trema_database import\
	get_trema_database
from routes import\
	create_routes

start_time = datetime.now()

bot_token = os.getenv('DISCORD_TOKEN')
if not bot_token:
    print('ERROR: Token var is missing: DISCORD_TOKEN')
    sys.exit(-1)

api_address = os.getenv('API_ADDRESS')
if not api_address:
	print('ERROR: API address var is missing: API_ADDRESS')
	sys.exit(-1)

api_port = os.getenv('API_PORT')
if not api_port:
	print('ERROR: API port var is missing: API_PORT')
	sys.exit(-1)

app = Quart(__name__)

intents = discord.Intents.default()
intents.members = True
trema = discord.Bot(intents=intents)

database = get_trema_database()

create_event_reactions(trema, database)
create_slash_cmds(trema, database, start_time)
create_routes(app, database, trema)

async def main():
    loop = asyncio.get_event_loop()

	# Start the bot and the API
    bot_coro = loop.create_task(trema.start(bot_token))
    api_coro = loop.create_task(app.run_task(host=api_address, port=api_port))

    await asyncio.gather(bot_coro, api_coro)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())