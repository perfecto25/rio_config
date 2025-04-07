
import os
import re
import sys

from functools import reduce
from loguru import logger


class Flex():
    def __init__(self):
        self.data = None

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
                logger.info("VAR VAR    ")
                var = value.split("@env")[1].strip()
                logger.debug(var)
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

        lines = config_text.strip().split('\n')

        try:
            for line in lines:
                line = line.strip()
                logger.info(f"line = {line}")

                ### skip comments
                if not line or line.startswith('#'):
                    continue

                ### check if line is a section header
                if line.startswith("[") and line.endswith("]"):
                    ### check if line is defining a template
                    if line.find("@template") != -1:
                        current_template = None
                        template_name = line.split("@template")[1].strip("[]").strip()
                        templates[template_name] = {}
                        current_template = template_name
                        logger.error(current_template)
                        current_section = templates[template_name]
                    else:
                        ### not defining a template, just section header line
                        current_template = None
                        section_header = line.strip("[]").split(":")
                        logger.info(f"section_header: {section_header}")
                        keys = self.create_nested_dict(section_header)
                        all_cfg_items.append(keys)
                        current_section = keys

#                        print_non_internal_vars()
                ### non section header line
                else:
                    logger.info(f"- current section {current_section}")
                    # apply template to section
                    if line.startswith("@use"):
                        template_name = line[4:].strip()
                        logger.warning(f"USING template {template_name}")
                        if template_name in templates and current_section is not None:
                            for template_key, template_val in templates[template_name].items():
                                self.add_to_last_element(current_section, template_key, template_val)

                    if '=' in line and current_section is not None:
                        
                        new_key, new_val = [part.strip() for part in line.split('=', 1)]
                        # if processing a Template, add to Template dict
                        if current_template:
                            templates[current_template][new_key] = new_val
                        else:
                        #     if new_val.startswith('@raw'):
                        #         logger.error(f"RAW RAW {new_val}")
                        #         new_val = new_val.split('@raw')[1]
                        #         #val = repr(val)[1:-1]
                        #         logger.error(f"newval {new_val}")
                            

                            # parse the section header and add keyname:keyval as a subhash
                            self.add_to_last_element(current_section, new_key, new_val)
                    

            merged = reduce(self.recursive_merge, all_cfg_items)
            return merged

        except (IndexError, TypeError) as err:
            print(f"\n[ERROR] unable to parse file line: {line}\n")
            raise Exception(str(err))
