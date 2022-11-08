import re


_PATTERN_MENTION = "@-"


def make_mention(text, mentionnable):
	"""
	Searches a text for occurrences of "@-" and replaces them with the given
	object's mention (@name or #name).

	Args:
		text (str): any text
		mentionnalbe: any object with attribute mention

	Returns:
		str: the given text with mentions of the mentionnable object.
	"""
	def _get_mention(match_obj):
		# The argument is not used.
		return mentionnable.mention

	formatted_text = re.sub(_PATTERN_MENTION, _get_mention, text)
	return formatted_text
