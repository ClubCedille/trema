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