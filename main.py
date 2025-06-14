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
import hypercorn.asyncio
from hypercorn.config import Config
from cogs.events import create_event_reactions
from cogs import create_slash_cmds
from db.database import get_trema_database
from routes import create_routes
from logger import logger
from prometheus_client import start_http_server

start_time = datetime.now()

bot_token = os.getenv('DISCORD_TOKEN')
if not bot_token:
    logger.error('ERROR: Token var is missing: DISCORD_TOKEN')
    sys.exit(-1)

api_address = os.getenv('API_ADDRESS')
if not api_address:
    logger.error('ERROR: API address var is missing: API_ADDRESS')
    sys.exit(-1)

api_port = os.getenv('API_PORT')
if not api_port:
    logger.error('ERROR: API port var is missing: API_PORT')
    sys.exit(-1)

github_token = os.getenv('GITHUB_TOKEN')

app = Quart(__name__)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
trema = discord.Bot(intents=intents)

database = get_trema_database()

create_event_reactions(trema, database)
create_slash_cmds(trema, database, start_time, github_token)
create_routes(app, database, trema)

start_http_server(9090)

async def run_quart_app(app, host, port):
    config = Config()
    config.bind = [f"{host}:{port}"]
    await hypercorn.asyncio.serve(app, config)

async def main():

    logger.info("Starting the bot and API")

    bot_coro = asyncio.create_task(trema.start(bot_token))
    api_coro = asyncio.create_task(run_quart_app(app, api_address, api_port))

    await asyncio.gather(bot_coro, api_coro)

if __name__ == '__main__':
    logger.info("Main application starting")
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(main())

        loop.run_forever()
    except Exception as e:
        logger.error(f"Unhandled exception in main application: {e}")
        raise
    finally:
        logger.info("Main application shutting down")
        loop.close()
