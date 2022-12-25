import asyncio
import discord


_ROLE_EVERYONE = "@everyone"


def get_channel_by_name(guild, channel_name):
	"""
	Given a guild and the name of one of its channels, this function provides
	the corresponding channel object. If the guild has more than one channel
	with that name, the first channel found is returned.

	Args:
		guild (discord.Guild): a Discord guild
		channel_name (str): the name of the wanted channel

	Returns:
		discord.abc.GuildChannel: a channel with the specified name or None if
			the guild does not have a channel with that name
	"""
	return discord.utils.get(guild.channels, name=channel_name)


def get_channel_name(guild, channel_id):
	"""
	Given a guild and the ID of one of its channels, this function provides the
	channel's name.

	Args:
		guild (discord.Guild): a Discord guild
		channel_id (int): the ID of one of guild's channels

	Returns:
		str: the given channel's name or None if guild does not have channel_id
	"""
	channel = guild.get_channel(channel_id)

	if channel is None:
		return None

	return channel.name


def get_member_by_name(guild, member_name):
	"""
	Given a guild and the name of one of its members, this function provides
	the corresponding member object. If the guild has more than one member
	with that name, the first member found is returned.

	Args:
		guild (discord.Guild): a Discord guild
		member_name (str): the name of the wanted member

	Returns:
		discord.abc.GuildChannel: a guild member with the specified name or
			None if the guild does not have a member with that name
	"""
	return discord.utils.get(guild.members, name=member_name)


def member_roles_are_default(member):
	"""
	Determines whether a server member does not have roles besides the default
	ones: @everyone and the member's name.

	Args:
		member (discord.member.Member): a server member

	Returns:
		bool: True if all of member's roles are default one, False otherwise
	"""
	member_name = member.name

	for role in member.roles:
		role_name = role.name

		if role_name != _ROLE_EVERYONE and role_name != member_name:
			return False

	return True


async def send_delayed_dm(user, message, delay, condition=None):
	"""
	Sends a direct message (DM) to the specified Discord user after a delay. If
	a condition is given, it is evaluated when the delay is up and it must
	return True for the message to be sent.

	Args:
		user (discord.abc.User): a Discord user
		message (str): the direct message to send to user
		delay (int): the time to wait, in seconds, before sending the message
		condition (function): a Boolean function that takes no argument. The
			message is sent if it is None or it returns True. Defaults to None.
	"""
	await asyncio.sleep(delay)

	if condition is None or condition():
		await user.send(message)
