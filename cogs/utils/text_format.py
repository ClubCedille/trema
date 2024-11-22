from discord import\
    TextChannel,\
    Color,\
    Embed

_SLASH = "/"
_MEMBER_MENTIONABLE = "[@-]"
_REQUEST_VALUE = "$"
_SPACE = " "

def make_mention(text, mention_dict, guild=None):
    """
    Searches a text for occurrences of placeholders and replaces them with 
    the mention of corresponding objects, including custom emojis.

    Args:
        text (str): The input text containing placeholders.
        mention_dict (dict): A dictionary where the key is the placeholder and 
                             the value is the object to mention.
        guild (discord.Guild, optional): The guild to search for custom emojis. Required for emoji replacement.

    Returns:
        str: The given text with mentions and custom emojis replaced.
    """
    if guild:
        emoji_dict = {f"{{!{emoji.name}}}": f"<:{emoji.name}:{emoji.id}>" for emoji in guild.emojis}
    else:
        emoji_dict = {}

    for placeholder, replacement in mention_dict.items():
        text = text.replace(placeholder, replacement)

    for emoji_placeholder, emoji_value in emoji_dict.items():
        text = text.replace(emoji_placeholder, emoji_value)

    return text



def generate_mention_dict(guild, newMember = None):
    mention_dict = {
        '{server}': guild.name,
        '{everyone}': '@everyone',
        '{here}': '@here'
    }

    # For mentionning a new member
    mention_dict['{newMember}'] = newMember.mention if newMember is not None else ''

    for member in guild.members:
        placeholder = f'{{{member.name}}}'
        mention_dict[placeholder] = member.mention

    for role in guild.roles:
        placeholder = f'{{&{role.name}}}'
        mention_dict[placeholder] = role.mention

    for channel in guild.channels:
        if isinstance(channel, TextChannel):
            placeholder = f'{{#{channel.name}}}'
            mention_dict[placeholder] = channel.mention

    return mention_dict

def _make_cmd_full_name(cmd):
	names = list()

	while cmd is not None:
		names.insert(0, cmd.name)
		cmd = cmd.parent

	full_name = _SLASH + _SPACE.join(names)

	return full_name

def _make_config_confirm_embed(title, updated_value, prev_value):
	confirm_embed = Embed(
		title=title,
		description=f"Nouvelle valeur:\n`{updated_value}`\n\nValeur précédente:\n`{prev_value}`",
		color=Color.green())
	return confirm_embed

def _make_config_display_embed(title, current_value):
	display_embed = Embed(
		title=title,
		description=f"Valeur actuelle: {current_value}",
		color=Color.green())
	return display_embed

def _make_config_error_embed(title, current_value, error_msg):
	error_embed = Embed(
		title=title,
		description=
			f"ERREUR!\n{error_msg}\n\nValeur actuelle: {current_value}",
		color=Color.red())
	return error_embed