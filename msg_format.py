import re

from discord_util import\
	get_channel_by_name,\
	get_member_by_name


_PATTERN_NAME = r"(\w)+"

# #channel
_PATTERN_CHANNEL = "#" + _PATTERN_NAME

# The member concerned by an event
_PATTERN_EVENT_MEMBER = "@-"

# @member
_PATTERN_MEMBER_NAME = "@" + _PATTERN_NAME

_PIPE = "|"
_FULL_PATTERN = _PATTERN_CHANNEL\
	+ _PIPE + _PATTERN_EVENT_MEMBER\
	+ _PIPE + _PATTERN_MEMBER_NAME
print(_FULL_PATTERN)


def format_message(message, event_member):
	guild = event_member.guild

	def _apply_fomrat(match_obj):
		match_str = match_obj.group()
		print(match_str)
		replacement = None

		if re.fullmatch(_PATTERN_CHANNEL, match_str):
			channel = get_channel_by_name(guild, match_str[1:])

			if channel is None:
				replacement = match_str
			else:
				replacement = channel.mention

		elif re.fullmatch(_PATTERN_EVENT_MEMBER, match_str):
			replacement = event_member.mention

		elif re.fullmatch(_PATTERN_MEMBER_NAME, match_str):
			guild_member = get_member_by_name(guild, match_str[1:])

			if guild_member is None:
				replacement = match_str
			else:
				replacement = guild_member.mention

		print(replacement)
		return replacement

	formatted_msg = re.sub(_FULL_PATTERN, _apply_fomrat, message)
	print(formatted_msg)
	return formatted_msg
