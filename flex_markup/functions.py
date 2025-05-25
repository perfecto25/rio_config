import re
import os
import sys
from loguru import logger
import ast


def remove_whitespace(text):
    """Removes all whitespace characters from a string."""
    return re.sub(r"\s+", "", text)


def create_nested_dict(lst):
    logger.info(f"LST {lst}")
    if not lst:
        return {}
    if len(lst) == 1:
        return {lst[0]: {}}
    return {lst[0]: create_nested_dict(lst[1:])}


def get_type(value):
    """checks if an integer, string, bool"""
    if not value:
        return
    logger.info(value)

    # List
    if value.startswith('[') and value.endswith(']') and ',' in value:
        logger.info(f"value is list >> {value}")
        value = value.strip("[").strip("]").strip()
        value = ''.join(value.split()).split(',')
        # for val in value:
        #     if any([val.startswith('"'), val.startswith("'")]) and any([val.endswith('"'), val.endswith("'")]):
        #         logger.debug("ANY")
        #         val = val.strip('"').strip("'")
        #         val = str(val)
        #     logger.debug(val)
        #     #val.replace("'", '"')
        # logger.success(val)

        # if integer is quoted, keep it a string

        # value = [x.strip('"') if x.startswith('"') else x for x in value]

        # if integer not quoted, turn it into int
        value = [int(x) if x.isdigit() else x for x in value]
        value = [x.strip('"') if not type(x) is int and x.startswith('"') else x for x in value]
        value = [x.strip("'") if not type(x) is int and x.startswith("'") else x for x in value]
        # remove empty elements, keep zeros
        value = [x for x in value if x is not None and x != '' and x != []]

        return value

    # String
    if value.startswith('"') or value.startswith("'"):
        logger.info("STR ")
        value = str(value).rstrip('"').rstrip("'").lstrip('"').lstrip("' ")
        return value

    # Integer
    try:
        value = int(value)
        logger.success(value)
        return value
    except (TypeError, ValueError):
        pass

    # Boolean
    if value in ["true", "True"]:
        return True
    if value in ["false", "False"]:
        return False

    # Float
    if re.match(r'^-?\d+\.\d+$', value):
        return float(value)

    return value


def deep_merge_pipe(dict1, dict2):
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_pipe(result[key], value)
        else:
            result[key] = value
    return result


def add_to_last_element(d, key, value):
    """ 
    inserts the key, value from non header section of config file, to the last element of the header section 
    ie, 

    [header.section]
    key = val

    >> will insert 

    {
        "header":
          "section": {
            "key": "val"
          }
    }

    """
    logger.info(f"getting {key}:{value}")
    logger.info(f"D = {d}")
    # Check if the current element is a dictionary
    if isinstance(d, dict):
        for sub_key in d:
            # Recurse into the sub-dictionary
            add_to_last_element(d[sub_key], key, value)
    else:
        # Base case: If it's not a dictionary, return
        # logger.info("from add to last element, NONE")
        # d[key] = value

        return

    # If the current dictionary has no further nested dictionaries, add the key-value pair
    if all(not isinstance(v, dict) for v in d.values()):
        d[key] = value

        # # handle lists
        # elif value.startswith('[') and value.endswith(']'):
        #     items = value[1:-1].split(',')
        #     d[key] = items

        # # handle env vars
        # elif value.startswith('@env'):
        #     var = value.split("@env")[1].strip()
        #     if '||' in var:
        #         env_var = var.split('||')[0].strip()
        #         default = var.split('||')[1].strip()
        #         value = os.getenv(env_var, default)
        #     else:
        #         value = os.getenv(var, "")
        #     d[key] = value
        # else:
        #     logger.debug(value)
        #     d[key] = value


def add_to_deepest_dict(d, new_key, new_value):
    def find_deepest(d, current_depth=0, max_depth=[0], target=[None]):
        is_leaf_dict = True
        for key, value in d.items():
            if isinstance(value, dict):
                is_leaf_dict = False
                find_deepest(value, current_depth + 1, max_depth, target)
        if is_leaf_dict and current_depth >= max_depth[0]:
            max_depth[0] = current_depth
            target[0] = d

    target = [None]
    max_depth = [0]
    find_deepest(d, 0, max_depth, target)
    if target[0] is not None:
        target[0][new_key] = new_value
    elif not d:
        d[new_key] = new_value


def set_nested_dict(ret, key_string, value):
    keys = key_string.split(".")
    logger.info(f"keys = {keys}")
    current = ret

    # Navigate or create nested dictionaries up to the second-to-last key
    for k in keys[:-1]:
        logger.info(f"k = {k}")
        # If the key doesn't exist, create an empty dictionary
        if k not in current:
            logger.error(f"current={current}")
            current[k] = {}
        current = current[k]

    # Set the value at the final key
    logger.debug(current)
    logger.debug(current[keys[-1]])
    current[keys[-1]] = value


def get_key(sections, ret):
    for key, content in sections:
        # check header key is quoted, strip quotes
        if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
            quote_char = key[:1]
            key = key.rstrip(quote_char).lstrip(quote_char)
            ret[key] = {}
        # check for escape char
        if r"\." in key and not ret:
            # generate keylist by replaceing escape dot with escape placeholder
            # to be able to split by actual dots
            key = key.replace(r'\.', '__flx__')
            keylist = key.split('.')
            # regenerate keylist and re-substitute eschape placeholder with escape dot
            keylist = [item.replace('__flx__', '.') for item in keylist]
            ret = create_nested_dict(keylist)
            # generate dict with header subkeys ie [key1.key2.key3]
        if '.' in key:
            keylist = key.split('.')
            ret = create_nested_dict(keylist)
