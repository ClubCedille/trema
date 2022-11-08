import asyncio

from discord_util import\
	member_roles_are_default,\
	send_delayed_dm

from msg_format import\
	format_message


_DELAY_SECS_15_MIN = 15 * 60


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
		welcome_chan = _get_welcome_chan(guild, trema_db)

		welcome_msg = trema_db.get_server_welcome_msg(guild_id)
		welcome_msg = format_message(welcome_msg, member)
		await welcome_chan.send(welcome_msg)

		# A reminder if the new member does not select a role
		reminder_msg = trema_db.get_server_reminder_msg(guild_id)
		if not member.bot and reminder_msg is not None:
			reminder_msg = format_message(reminder_msg, member)
			msg_condition = lambda: member_roles_are_default(member)
			reminder_task = asyncio.create_task(send_delayed_dm(
				member, reminder_msg, _DELAY_SECS_15_MIN, msg_condition))
			await asyncio.wait([reminder_task])

	@trema_bot.event
	async def on_member_remove(member):
		guild = member.guild
		guild_id = guild.id
		leave_msg = trema_db.get_server_leave_msg(guild_id)
		if leave_msg is not None:
			welcome_chan = _get_welcome_chan(guild, trema_db)
			leave_msg = format_message(leave_msg, member)
			await welcome_chan.send(leave_msg)

	@trema_bot.event
	async def on_ready():
		print(f"{trema_bot.user} fonctionne.")
