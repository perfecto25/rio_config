import re
import os
import sys
from loguru import logger 
  
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
    ## String
    if value.startswith('"') or value.startswith("'"):
        logger.info("STR ")
        value = str(value).rstrip('"').rstrip("'").lstrip('"').lstrip("' ")
        return value
    
    ## Integer
    try:
        value = int(value)
        logger.success(value)
        return value
    except (TypeError, ValueError):
        pass

    ## Boolean
    if value in ["true", "True"]: 
        return True
    if value in ["false", "False"]:
        return False

    ## Float
    if re.match(r'^-?\d+\.\d+$', value):
        return float(value)
    
    return value

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
        #logger.info("from add to last element, NONE")
        #d[key] = value
    
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

def check_kv_pattern(line, section_dict, multiline_comment=False, multiline_list=False):
    """checks if given value is in key=value pattern"""
    kv_pattern = re.compile(r'^\s*([^=]+?)\s*=\s*(.+?)\s*$')  # Matches key = value
    kv_match = kv_pattern.match(line)
    if kv_match:
        logger.error(section_dict)
        multiline_comment = False
        multiline_list = False
        key = kv_match.group(1).strip()
        value = kv_match.group(2).strip()
        logger.debug(f"VALUE {value}")
        value = get_type(value)
      
        section_dict = add_to_last_element(section_dict, key, value)
        return [section_dict, multiline_comment, multiline_list]
    else:
        return []

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

def parse_section(key, val, ret):
    """generate return dict with section's keys and values"""
    
    section_dict = {}
    

    # check header key is quoted, strip quotes
    if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
        quote_char = key[:1]
        key = key.rstrip(quote_char).lstrip(quote_char)
        section_dict[key] = {}
    
    # check for escape char
    if r"\." in key and not section_dict:
        # generate keylist by replaceing escape dot with escape placeholder
        # to be able to split by actual dots
        key = key.replace(r'\.', '__flx__')
        keylist = key.split('.')

        # regenerate keylist and re-substitute eschape placeholder with escape dot
        keylist = [item.replace('__flx__', '.') for item in keylist]
        section_dict = create_nested_dict(keylist)

    # generate dict with header subkeys ie [key1.key2.key3]
    if '.' in key and not section_dict:
        keylist = key.split('.')
        section_dict = create_nested_dict(keylist)
    
    if not section_dict:
        section_dict[key] = {}

    # process section values and convert to k=v structure
    multiline_comment = False 
    multiline_list = False
    logger.debug(f"section_dict = {section_dict}")
    ## split section Value into valsections delimited by key = value
    pattern = r'^\s*(\w+)\s*=\s*(.*?)\s*(?=(?:\n\s*\w+\s*=|\Z))'
    sections = re.findall(pattern, val, re.MULTILINE | re.DOTALL)
    logger.debug(sections)

    for section_key in section_dict.keys():
        logger.error(section_key)
    for section in sections:
        k = section[0]
        v = get_type(section[1])
        logger.info(f"KV = {k}:{v}")
        logger.debug(f"SectionDict = {section_dict}")

        logger.debug(section_dict.keys())
        add_to_deepest_dict(section_dict, k, v)
        #section_dict = add_to_last_element(section_dict, k, v)
    logger.success(section_dict)
        #current_val = check_kv_pattern(key, value, section_dict)
    # sys.exit()

    # for line in val.split('\n'):
    #     if not line or line.startswith('#') or line.isspace():
    #         logger.success(f"skipping {line}")
    #         continue
    #     line = line.rstrip('\r\n')  ## remove newline chars
    #     line = line.replace('\t', ' ') ## replace tabs w spaces

    #     current_val = check_kv_pattern(line, section_dict, multiline_comment=multiline_comment, multiline_list=multiline_list)
    #     if current_val:
    #         logger.debug(current_val)
    #     logger.debug(line)



    logger.warning(section_dict)
    ret = ret|section_dict
    # if key not in ret:
    #     ret[key] = {}
    
    

    return ret
