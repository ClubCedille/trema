import re


# The member concerned by an event
_PATTERN_EVENT_MEMBER = "@-"


def format_message(message, event_member):
	def _apply_fomrat(match_obj):
		print(match_obj.group())
		return event_member.mention

	formatted_msg = re.sub(_PATTERN_EVENT_MEMBER, _apply_fomrat, message)
	print(formatted_msg)
	return formatted_msg
