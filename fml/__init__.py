
import os
import json
import re
import sys
import copy
from functools import reduce
from loguru import logger
# import pdb
from .functions import replace_shell_vars, substitute_instance, parse_value

class Fml():
    def __init__(self):
        self.data = None
    
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
                        template_name = line.split("@template")[1].strip("[]").strip()
                        templates[template_name] = {}
                        current_section = templates[template_name]
                    else:
                        section_header = line.strip("[]").split(":")
                        logger.info(f"section_header: {section_header}")
    #                    result = reduce(lambda x, y: {y: x}, section_header[::-1])
                        keys = self.create_nested_dict(section_header)
                        #config[keys] = {}
                        all_cfg_items.append(keys)
                        logger.debug(type(keys))
                        logger.debug(keys)
                        # cycle thru section_header and create dicts for each key
                        # [check:filesystem:opt:blah]
                        # keychain = [first]
                        # first = section_header[:1]  #  'check'
                        # config[first] = {}  'config['check'] = {}'
                        # last is val
                        # section_header.pop(last)  # remove last element from list - thats the final value
                        # while len(section_header > 1)
                        #  keychain = []
                        #  key = sectoin_header[last] 'key=blah'
                           # config[first][key]

                ## apply template to section
                if line.startswith("@use"):
                    logger.debug(f"@USE sec headder {section_header}")


            logger.debug(templates)
            merged = reduce(self.recursive_merge, all_cfg_items)
            logger.info(type(merged))
            return merged   

        except (IndexError, TypeError) as err:
            print(f"\n[ERROR] unable to parse file line: {line}\n")
            raise Exception(str(err))
