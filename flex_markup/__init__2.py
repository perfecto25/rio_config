
import os
import re
import sys

from functools import reduce
from loguru import logger


class Flex():
    def __init__(self):
        self.data = None

    def merge_dicts(self, dict1, dict2):
        merged = dict1.copy()
        for key, value in dict2.items():
            if key in merged:
                # Handle duplicate keys, e.g., combine values or keep the original
                merged[key] = [merged[key], value] #Example: combine values in a list
            else:
                merged[key] = value
        return merged

    def add_to_last_element(self, d, key, value):
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
                self.add_to_last_element(d[sub_key], key, value)
        else:
            # Base case: If it's not a dictionary, return
            return

        # If the current dictionary has no further nested dictionaries, add the key-value pair
        if all(not isinstance(v, dict) for v in d.values()):

            # handle strings
            if value.startswith('"') and value.endswith('"'):
                value = value.rstrip('"').lstrip('"')
                d[key] = str(value)

            # handle bools
            if value.lower() == 'true':
                d[key] = True
            elif value.lower() == 'false':
                d[key] = False

            # handle floats
            elif re.match(r'^-?\d+\.\d+$', value):
                d[key] = float(value)

            # handle ints
            elif re.match(r'^-?\d+$', value):
                d[key] = int(value)

            # handle lists
            elif value.startswith('[') and value.endswith(']'):
                items = value[1:-1].split(',')
                d[key] = items

            # handle env vars
            elif value.startswith('@env'):
                var = value.split("@env")[1].strip()
                if '||' in var:
                    env_var = var.split('||')[0].strip()
                    default = var.split('||')[1].strip()
                    value = os.getenv(env_var, default)
                else:
                    value = os.getenv(var, "")
                d[key] = value
            else:
                logger.debug(value)
                d[key] = value

    def create_nested_dict(self, lst):
        if not lst:
            return {}
        if len(lst) == 1:
            return {lst[0]: {}}
        return {lst[0]: self.create_nested_dict(lst[1:])}

    def recursive_merge(self, d1, d2):
        result = d1.copy()
        for key, value in d2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.recursive_merge(result[key], value)
            else:
                result[key] = value
        return result



    

    def parse(self, config_text):
        config = {}
        templates = {}
        all_cfg_items = []
        current_section = None
        apply_template = None
        current_template = None
        section_header = None

        ret = {}
        template = None
        topkey = None

        lines = config_text.strip().split('\n')

        try:
            for line in lines:
                line = line.strip()
                logger.info(f""" 
line : {line},
curr section: {current_section} 
current template: {current_template}
all templates: {templates} 
                        """)

                # skip comments
                if not line or line.startswith('#'):
                    continue

                # topkey or Template line
                if line.startswith("[") and line.endswith("]"):
                    # clear flags
                    current_template = None
                    topkey = None

                    if line.find("@template") != -1:
                        logger.warning("TEMPLATE")
                        template_name = line.split("@template")[1].strip("[]").strip()
                        templates[template_name] = {}
                        current_template = template_name
                        logger.debug(templates)
                        current_section = templates[template_name]
                        continue
                    
                    # regular topkey ie [one:two:three]
                    topkey = None
                    current_section = None
                    topkey = line.strip("[]").split(":")
                    current_section = self.create_nested_dict(topkey)
                
                    # merge ret with current_section dict
                    ret = self.merge_dicts(ret, current_section)

                    logger.warning(current_section)
                    continue
                logger.info(current_section)

                # line is part of template
                if '=' in line and current_template:
                    new_key, new_val = [part.strip() for part in line.split('=', 1)]
                    templates[current_template][new_key] = new_val
                    continue

                # topkey: subhash
                if '=' in line and current_section:
                    
                    logger.debug(topkey)    
                    new_key, new_val = [part.strip() for part in line.split('=', 1)]
                    
                    if not new_key:
                        continue  # drop line if key is empty

                    self.add_to_last_element(current_section, new_key, new_val)
                    continue

                if line.startswith("@use"):
                    template_name = line[4:].strip()
                    logger.warning(f"USING template {template_name}")
                    if template_name in templates and current_section is not None:
                        for template_key, template_val in templates[template_name].items():
                            self.add_to_last_element(current_section, template_key, template_val)
                            continue

                else:
                    # topkey: value
                    self.add_to_last_element(topkey, new_key, new_val)
                    ret[topkey] = line

            return ret

 #           merged = reduce(self.recursive_merge, all_cfg_items)
  #          return merged

        except (IndexError, TypeError) as err:
            print(f"\n[ERROR] unable to parse file line: {line}\n")
            raise Exception(str(err))
