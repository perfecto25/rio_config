import re

def remove_whitespace(text):
    """Removes all whitespace characters from a string."""
    return re.sub(r"\s+", "", text)