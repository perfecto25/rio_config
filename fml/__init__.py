
import os
import json
import re
import sys
import copy
from loguru import logger
# import pdb
from .functions import replace_shell_vars, substitute_instance, parse_value


logger.remove()
logger.add(sys.stderr, level="DEBUG")

class Fml():
    def __init__(self):
        self.data = None

    def parse(self, config_text):
        config = {}
        templates = {}
        current_section = None
        apply_template = None

        lines = config_text.strip().split('\n')

        try:
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                section_match = re.match(r'\[(.*?)(?::(\w+))?\]', line)
                if section_match:
                    section_name = section_match.group(1)
                    instance_id = section_match.group(2)
                    logger.debug(f"section name {section_name}")
                    logger.debug(f"section match {section_match}")
                    apply_template = None

                    if section_name.startswith('@template'):
                        template_name = section_name[9:].strip()
                        templates[template_name] = {}
                        current_section = templates[template_name]
                    elif instance_id:
                        base_name = section_name.split(':')[0]
                        if base_name not in config:
                            config[base_name] = {}
                        if instance_id not in config[base_name]:
                            config[base_name][instance_id] = {}
                        current_section = config[base_name][instance_id]
                    else:
                        if section_name not in config:
                            config[section_name] = {}
                        current_section = config[section_name]
                    continue

                if line.startswith('@use'):
                    template_name = line[4:].strip()
                    if template_name in templates and current_section is not None:
                        template_config = copy.deepcopy(templates[template_name])
                     #   print(f"template config {template_config}")
                        instance_config = substitute_instance(template_config, current_section.get('__instance_id', ''))
                        current_section.update(instance_config)
                    continue

                if '=' in line and current_section is not None:
                    #print(f"current_section {current_section}")
                    key, value = [part.strip() for part in line.split('=', 1)]
                    target = current_section
                    keys = key.split('.')
                    for i, k in enumerate(keys[:-1]):
                        if k not in target:
                            target[k] = {}
                        target = target[k]
                    final_key = keys[-1]
                    if instance_id and '__instance_id' not in current_section:
                        current_section['__instance_id'] = instance_id
                    target[final_key] = parse_value(value)

            final_config = replace_shell_vars(config)
            for section in final_config.values():
                for instance in section.values():
                    if isinstance(instance, dict):
                        instance.pop('__instance_id', None)
            return final_config
        except (IndexError, TypeError) as err:
            print(f"\n[ERROR] unable to parse file line: {line}\n")
            raise Exception(str(err))
        
    
