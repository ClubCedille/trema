import asyncio

from discord_util import\
	member_roles_are_default,\
	send_delayed_dm

from discord import TextChannel

from text_format import\
	make_mention


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
		mention_dict = {
			'{member}': member.mention,
			'{username}': member.name,
			'{server}': guild.name,
			'{everyone}': '@everyone',
			'{here}': '@here'
    	}
		for role in guild.roles:
			placeholder = f'{{&{role.name}}}'
			mention_dict[placeholder] = role.mention

		for channel in guild.channels:
			if isinstance(channel, TextChannel):
				placeholder = f'{{#{channel.name}}}'
				mention_dict[placeholder] = channel.mention
	    
		welcome_msg = make_mention(welcome_msg, mention_dict)
		await welcome_chan.send(welcome_msg)

		# A reminder if the new member does not select a role
		reminder_msg = trema_db.get_server_reminder_msg(guild_id)
		if not member.bot and reminder_msg is not None:
			reminder_msg = make_mention(reminder_msg, member)
			reminder_delay = trema_db.get_server_reminder_delay(guild_id)
			msg_condition = lambda: member_roles_are_default(member)
			reminder_task = asyncio.create_task(send_delayed_dm(
				member, reminder_msg, reminder_delay, msg_condition))
			await asyncio.wait([reminder_task])

	@trema_bot.event
	async def on_member_remove(member):
		guild = member.guild
		guild_id = guild.id
		leave_msg = trema_db.get_server_leave_msg(guild_id)
		if leave_msg is not None:
			welcome_chan = _get_welcome_chan(guild, trema_db)
			leave_msg = make_mention(leave_msg, member)
			await welcome_chan.send(leave_msg)

	@trema_bot.event
	async def on_ready():
		print(f"{trema_bot.user} fonctionne.")
