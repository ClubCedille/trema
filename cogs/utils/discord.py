import asyncio
import discord
import os
from datetime import datetime, timezone, timedelta


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


async def send_delayed_dm(user, message, delay, condition=None, message_type='text', filepath=None):
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
		message_type (str): the type of the message ('text', 'embed', 'file')
	"""
	await asyncio.sleep(delay)

	if condition is None or condition():
		if message_type == 'embed':
			await user.send(embed=message)
		elif message_type == 'file':
			await user.send(file=message)
			os.remove(filepath)
		else:
			await user.send(message)

async def send_reminder(reminder_id, trema_bot, trema_db):
	try:
		reminder_data = trema_db.get_reminder(reminder_id)
		if not reminder_data:
			print(f"Erreur: Rappel {reminder_id} introuvable.")
			return

		scheduled_time = datetime.fromtimestamp(reminder_data['scheduled_time'], timezone.utc)
		now = datetime.now(timezone.utc)
		delay_seconds = (scheduled_time - now).total_seconds()
		if delay_seconds > 0:
			while delay_seconds > 3600:
				sleep_time = delay_seconds * 2 / 3
				await asyncio.sleep(sleep_time)

				now_utc = datetime.now(timezone.utc)
				delay_seconds = (scheduled_time - now_utc).total_seconds()

			if delay_seconds > 0:
				await asyncio.sleep(delay_seconds)

		current_status = trema_db.get_reminder_status(reminder_id)
		if current_status != 'pending':
			return
		trema_db.update_reminder_status(reminder_data['_id'], 'sent')

		guild = trema_bot.get_guild(reminder_data['guild_id'])
		if guild is None:
			return

		creator = await trema_bot.fetch_user(reminder_data['creator_id'])
		public = reminder_data.get('public', True)

		if public:
			confirmation_channel = guild.get_channel(reminder_data['confirmation_channel_id'])
			if confirmation_channel is None:
				try:
					await creator.send(f"Voici votre rappel pour le message: {reminder_data['message_link']}")
				except discord.Forbidden:
					pass
				return

			confirmation_message = await confirmation_channel.fetch_message(reminder_data['confirmation_message_id'])
			if confirmation_message is None:
				try:
					await creator.send(f"Voici votre rappel pour le message: {reminder_data['message_link']}")
				except discord.Forbidden:
					pass
				return

			reaction = discord.utils.get(confirmation_message.reactions, emoji='✅')
			if reaction:
				users = await reaction.users().flatten()
				users = [user for user in users if user.id != trema_bot.user.id]

				for user in users:
					try:
						await user.send(f"Voici votre rappel pour le message: {reminder_data['message_link']}")
					except discord.Forbidden:
						pass
			try:
				await creator.send(f"Voici votre rappel pour le message: {reminder_data['message_link']}")
			except discord.Forbidden:
				pass
		else:
			try:
				await creator.send(f"Voici votre rappel pour le message: {reminder_data['message_link']}")
			except discord.Forbidden:
				pass
	except Exception as e:
		print(f"Erreur lors de l'envoi du rappel: {e}")

def find_role_in_guild(guild, role_name):
	"""
	Given a guild and a role name, this function returns the role object with
	the specified name. The search is case-insensitive.
	"""
	for role in guild.roles:
		if role_name.lower() == role.name.lower():
			return role
	return None