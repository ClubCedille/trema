import asyncio
from cogs.utils.discord import\
	member_roles_are_default,\
	send_delayed_dm,\
	send_reminder

from cogs.utils.text_format import\
	make_mention,\
	generate_mention_dict

from logger import logger

DEFAULT_WELCOME_MSG_TEMPLATE = "Hey {newMember}! Bienvenue au {server}.\n" + \
    "Pour accéder au reste du serveur et interagir avec le bot, " + \
    "utilise la commande `/request join` !"

def _get_welcome_chan(guild, trema_db):
	guild_id = guild.id
	welcome_chan_id = trema_db.get_server_welcome_chan_id(guild_id)
	welcome_chan = guild.get_channel(welcome_chan_id)
	return welcome_chan

def create_event_reactions(trema_bot, trema_db):
	@trema_bot.event
	async def on_guild_join(guild):
		trema_db.register_server(guild)

	@trema_bot.event
	async def on_member_join(member):
		guild = member.guild
		guild_id = guild.id

		try:
			welcome_chan = _get_welcome_chan(guild, trema_db)
			if welcome_chan is None:
				raise Exception("Welcome channel not found.")
		except Exception as e:
			logger.error(f"Error fetching welcome channel: {e}")
			welcome_chan = guild.system_channel

		try:
			welcome_msg = trema_db.get_server_welcome_msg(guild_id)
			if welcome_msg is None:
				welcome_msg = DEFAULT_WELCOME_MSG_TEMPLATE.format(
					newMember=member.display_name,
					server=guild.name
				)
			else:
				welcome_msg = make_mention(welcome_msg, generate_mention_dict(guild, member))
		except Exception as e:
			logger.error(f"Error fetching welcome message: {e}")
			welcome_msg = DEFAULT_WELCOME_MSG_TEMPLATE.format(
				newMember=member.display_name,
				server=guild.name
			)

		if welcome_chan:
			await welcome_chan.send(welcome_msg)

		try:
			reminder_msg = trema_db.get_server_reminder_msg(guild_id)
			if not member.bot and reminder_msg is not None:
				reminder_msg = make_mention(reminder_msg, generate_mention_dict(guild, member))
				reminder_delay = trema_db.get_server_reminder_delay(guild_id)
				msg_condition = lambda: member_roles_are_default(member)
				reminder_task = asyncio.create_task(send_delayed_dm(
					member, reminder_msg, reminder_delay, msg_condition))
				await asyncio.wait([reminder_task])
		except Exception as e:
			logger.error(f"Error fetching reminder message: {e}")

	@trema_bot.event
	async def on_member_remove(member):
		guild = member.guild
		guild_id = guild.id
		leave_msg = trema_db.get_server_leave_msg(guild_id)
		if leave_msg is not None:
			mention_dict = generate_mention_dict(guild, member)
			leave_msg = make_mention(leave_msg, mention_dict)
			welcome_chan = _get_welcome_chan(guild, trema_db)
			await welcome_chan.send(leave_msg)

	@trema_bot.event
	async def on_ready():
		logger.info('{0.user} fonctionne.'.format(trema_bot))

		for guild in trema_bot.guilds:
			if not trema_db._id_exists(guild.id, "server"):
				logger.info(f"Server {guild.name} (ID: {guild.id}) not found in the database. Registering...")
				trema_db.register_server(guild)
			else:
				logger.info(f"Server {guild.name} (ID: {guild.id}) is already registered.")

		reminders = trema_db.get_pending_reminders()

		for reminder in reminders:
			asyncio.create_task(send_reminder(reminder, trema_bot, trema_db))

