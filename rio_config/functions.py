import re
import os

def create_nested_dict(lst):
    if not lst:
        return {}
    if len(lst) == 1:
        return {lst[0]: {}}
    return {lst[0]: create_nested_dict(lst[1:])}


def get_env_var(value):
    """Replace @env ENV_VAR || 'fallback' with environment variable or fallback."""
    if not value:
        return
    if '@env' not in value:
        return value

    fallback = None
    value = value.strip('@env').strip()
    
    if '||' in value:
        try:
            fallback = value.split('||')[1].strip()
            value = value.split('||')[0].strip()                
        except IndexError:
            pass
    val = os.environ.get(value, fallback)
    if val:
        val.strip()
    return val

def get_type(value):
    """checks if an integer, string, bool"""
    if not value:
        return

    # List
    if value.startswith('[') and value.endswith(']') and ',' in value:
        value = value.strip("[").strip("]").strip()
        value = ''.join(value.split()).split(',')

        # if integer not quoted, turn it into int
        value = [int(x) if x.isdigit() else x for x in value]
        value = [x.strip('"') if type(x) is not int and x.startswith('"') else x for x in value]
        value = [x.strip("'") if type(x) is not int and x.startswith("'") else x for x in value]
        # remove empty elements, keep zeros
        value = [x for x in value if x is not None and x != '' and x != []]
        return value

    # String
    if value.startswith('"') or value.startswith("'"):
        value = str(value).rstrip('"').rstrip("'").lstrip('"').lstrip("' ")
        return value

    # Integer
    try:
        value = int(value)
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
    # Check if the current element is a dictionary
    if isinstance(d, dict):
        for sub_key in d:
            # Recurse into the sub-dictionary
            add_to_last_element(d[sub_key], key, value)
    else:
        return

    # If the current dictionary has no further nested dictionaries, add the key-value pair
    if all(not isinstance(v, dict) for v in d.values()):
        d[key] = value

def remove_use_keys(d):
    if isinstance(d, dict):
        return {k: remove_use_keys(v) for k, v in d.items() if k != "@use"}
    elif isinstance(d, list):
        return [remove_use_keys(item) for item in d]
    return d

def set_last_key(d, value):
    """ sets value on last key of nested dict """
    current = d
    parent = None
    last_key = None
    while current and isinstance(next(iter(current.values())), dict):
        parent = current
        last_key = next(iter(current.keys()))
        current = next(iter(current.values()))

    # Set the value at the last key
    if parent is not None and last_key is not None:
        parent[last_key] = value
    
def extract_before_comment(line):
    # Pattern to match quoted or unquoted string before optional comment
    pattern = r'^\s*(?:"(.*?)"|\'(.*?)\'|([^#]*?))\s*(?:#.*)?$'
    match = re.match(pattern, line)
    if match:
        # Return the first non-None group: double-quoted, single-quoted, or unquoted
        return next(group for group in match.groups() if group is not None)
    return None

def remove_comments(line):
    # unquoted string with comment at end of the line
    if not line.startswith('[') and not line.startswith('"') and not line.endswith('"') and "#" in line:
        sections = line.split("#")
        return sections[0].strip()

    # multi line array ending bracket with comment at end
    elif line.startswith('[') and "#" in line:
        pattern = r'^(.*?)(?:#.*)?$'
        match = re.match(pattern, line, re.DOTALL)
        if match:
            return match.group(1).rstrip()

    # quoted string with comments at end of the line, only return the part thats quoted
    elif line.startswith('"') and not line.endswith('"') and "#" in line:
        pattern = r'^\s*"(.*?)"\s*(?:#.*)?$'
        match = re.match(pattern, line)
        if match:
            return match.group(1)
        else:
            return line
    else:
        return line

def check_syntax(content):
    """ parses all lines and errors out on bad syntax, removes leading spaces and tabs """
    cleaned = ""
    bracket_start = False
    for line in content.split('\n'):
        cleaned = cleaned + line.lstrip() + '\n'
        if "@use" in line and "=" not in line:
            raise Exception(f"""
            @use declaration must be in form of '@use = MyTemplateName'
            check for missing equal sign on this line >> {line} 
            """)
        
        if "#" in line:
            line = remove_comments(line)

        if line.startswith("[") and not line.endswith("]"):
            bracket_start = True
        if not line.startswith("[") and line.endswith("]"):
            bracket_start = False

        if ":" in line and bracket_start:
            line = line.replace("'", '"')
            if not line.startswith('"') and not line.endswith('"'):
                raise Exception(f"unquoted : symbol inside an Array declaration on line >> {line}")

    return cleaned