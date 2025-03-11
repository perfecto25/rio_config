#!/usr/bin/python3

import os
import json
import re
import copy

# import pdb


def parse_scm(config_text):
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

                print(f"section name {section_name}")
                print(f"section match {section_match}")
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
                    print(f"template config {template_config}")
                    instance_config = substitute_instance(template_config, current_section.get('__instance_id', ''))
                    current_section.update(instance_config)
                continue

            if '=' in line and current_section is not None:
                print(f"current_section {current_section}")
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
        print(f"\n[ERROR] unable to parse config file line: {line}\n")
        raise Exception(str(err))

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
    print(f"- Comment {comment}")
    if value.startswith('[') and value.endswith(']'):
        items = value[1:-1].split(',')
        print(f"--1-- {items}")
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

    print(f"PRE val {value}")
    if comment:
        value = value.split("#")[0]
    print(f"POST val {value}")
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


class Fml():
    def __init__(self):
        

if __name__ == "__main__":
    # pdb.set_trace()
    with open("p2.jaml") as file:
        data = file.read()

    os.environ['DOMAIN'] = 'example.com'
    os.environ['HOME'] = '/home/user'
    try:
        fml = Fml()
        result = fml.parse(data)

        result = parse_scm(data)
    except (IndexError, TypeError) as err:
        print("[ERROR] unable to parse config file")
        raise Exception(str(err))
 #   print(result["app"])
 #   print(json.dumps(result, indent=2))
