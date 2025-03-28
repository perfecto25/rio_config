import re
import os
import inspect
from loguru import logger

def print_non_internal_vars():
    """Prints the names and values of all non-internal variables in the current scope."""
    frame = inspect.currentframe().f_back
    variables = frame.f_locals
    
    for name, value in variables.items():
        if not name.startswith('_'):
            logger.debug(f"{name} = {value}")


def substitute_instance(template, instance_id):
    """Create a copy of template with $INSTANCE replaced"""
    def replace_instance(obj):
        if isinstance(obj, dict):
            return {k: replace_instance(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_instance(item) for item in obj]
        elif isinstance(obj, str):
            return obj.replace('$INSTANCE', instance_id)
        return obj
    return replace_instance(template)


def parse_value(value):
    """Convert string value to appropriate Python type"""
    value = value.strip()

    # Handle hash syntax (e.g., "key: val" or "key1: val1, key2: val2")
    if ':' in value and not value.startswith('(') and not value.startswith('['):
        hash_dict = {}
        pairs = value.split(',')
        for pair in pairs:
            if ':' in pair:
                k, v = [part.strip() for part in pair.split(':', 1)]
                hash_dict[k] = parse_value(v)  # Recursively parse value
        return hash_dict if hash_dict else value

    # check if theres a comment on the line
    comment = False
    if not all([value.startswith('"'),  value.endswith('"')]):    
        comment = True if "#" in value else False

    # Handle JSON-like list syntax
    if value.startswith('[') and value.endswith(']'):
        items = value[1:-1].split(',')
        return [parse_value(item.strip()) for item in items if item.strip()]

    # Handle space-separated list syntax
    if value.startswith('(') and value.endswith(')'):
        items = value[1:-1].split()
        return [parse_value(item) for item in items if item]

    # Handle booleans
    if value.lower() == 'true':
        return True
    if value.lower() == 'false':
        return False

    # Handle numbers
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        pass

    # Handle strings
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]

#    print(f"PRE val {value}")
    if comment:
        value = value.split("#")[0]
 #   print(f"POST val {value}")
    return value



def replace_shell_vars(obj):
    """Replace shell variables with environment values"""
    if isinstance(obj, dict):
        return {k: replace_shell_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_shell_vars(item) for item in obj]
    elif isinstance(obj, str):
        def replace_var(match):
            var_name = match.group(1)
            return os.environ.get(var_name, f"${var_name}")
        return re.sub(r'\$(\w+)', replace_var, obj)
    return obj
