from discord import\
    TextChannel,\
    Color,\
    Embed

_SLASH = "/"
_SPACE = " "

def make_mention(text, mention_dict):
    """
    Searches a text for occurrences of placeholders and replaces them with 
    the mention of corresponding objects.

    Args:
        text (str): any text
        mention_dict (dict): a dictionary where the key is the placeholder and 
        the value is the object to mention.

    Returns:
        str: the given text with mentions replaced.
    """
    for placeholder, mention in mention_dict.items():
            text = text.replace(placeholder, mention)
    return text

def generate_mention_dict(guild):
    mention_dict = {
        '{member}': '{member}',  
        '{server}': guild.name,
        '{everyone}': '@everyone',
        '{here}': '@here'
    }

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