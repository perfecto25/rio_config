
import os
import json
import re
import sys
import copy
from functools import reduce
from loguru import logger
# import pdb
from .functions import replace_shell_vars, substitute_instance, parse_value, print_non_internal_vars

class Fml():
    def __init__(self):
        self.data = None
    
    def create_nested_dict(self, lst):
        if not lst:
            return {}
        if len(lst) == 1:
            return { lst[0]: {} }
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

                if not line or line.startswith('#'):
                    continue

                # check if section header
                if line.startswith("[") and line.endswith("]"):
                    
                    if line.find("@template") != -1:
                        current_template = None
                        template_name = line.split("@template")[1].strip("[]").strip()
                        templates[template_name] = {}
                        current_template = template_name
                        logger.error(current_template)
                        current_section = templates[template_name]
                    else:
                        current_template = None
                        section_header = line.strip("[]").split(":")
                        logger.info(f"section_header: {section_header}")
                        keys = self.create_nested_dict(section_header)
                        all_cfg_items.append(keys)
                        current_section = keys

#                        print_non_internal_vars()
                # non section header line
                else: 
                    logger.info(f"- current section {current_section}")
                    ## apply template to section
                    if line.startswith("@use"):
                        template_name = line[4:].strip()
                        logger.warning(f"USING template {template_name}")
                        if template_name in templates and current_section is not None:
                            for template_key, template_val in templates[template_name].items():
                                current = current_section
                                for section_key in section_header:
                                    logger.info(f"<<<< current  {current}, current_section {current_section}, section_key {section_key}")
                                    # create empty dict if doesnt exist
                                    current = current.setdefault(section_key, {})
                                    current[template_key] = template_val
                                    logger.info(current)
                            # template_config = copy.deepcopy(templates[template_name])
                            # logger.debug(template_config)
                    

                    if '=' in line and current_section is not None:
                        logger.debug("81 =  ")
                    #print(f"current_section {current_section}")
                        new_key, new_val = [part.strip() for part in line.split('=', 1)]
                        logger.success(current_template)
                        logger.success(current_section)    
                        # if processing a Template, add to Template dict
                        if current_template:
                            logger.warning("x")
                            templates[current_template][new_key] = new_val
                        else:
                            # parse the section header and add keyname:keyval as a subhash
                            current = current_section
                            for key in section_header:
                                # create empty dict if doesnt exist
                                current = current.setdefault(key, {})
                            current[new_key] = new_val
                            logger.error(all_cfg_items)
                        if current_template:     
                            logger.warning(templates)
#                    logger.debug(f"SEC LINE {line}, current section {current_section}")



            merged = reduce(self.recursive_merge, all_cfg_items)

            return merged   

        except (IndexError, TypeError) as err:
            print(f"\n[ERROR] unable to parse file line: {line}\n")
            raise Exception(str(err))
