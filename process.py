#!/bin/python3
import os
import re
import json


class SimplexParser:
#    __slots__ = ("filename")

    def __init__(self):
        self.config = {}
        self.templates = {}
        self.current_group = None
        self.current_subgroup = None
        print("Initialized self.config:", self.config)

    def parse_value(self, value):
        value = value.strip()
        if value.startswith('[') and value.endswith(']'):
            items = []
            current = ''
            depth = 0
            for char in value[1:-1]:
                if char == '[':
                    depth += 1
                    current += char
                elif char == ']':
                    depth -= 1
                    current += char
                elif char == ',' and depth == 0:
                    items.append(self.parse_value(current))
                    current = ''
                else:
                    current += char
            if current.strip():
                items.append(self.parse_value(current))
            return items
        if value.startswith('{') and value.endswith('}'):
            hash_dict = {}
            for pair in value[1:-1].split(','):
                k, v = pair.split(maxsplit=1)
                hash_dict[k] = self.parse_value(v)
            return hash_dict
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
        if re.match(r'^-?\d+\.\d+$', value):
            return float(value)
        if re.match(r'^-?\d+$', value):
            return int(value)
        while '${' in value:
            start = value.index('${')
            end = value.index('}', start)
            var = value[start+2:end]
            default = var.split(':-')[1] if ':-' in var else ''
            var_name = var.split(':-')[0]
            value = value[:start] + os.getenv(var_name, default) + value[end+1:]
        return value

    def parse(self, filename):

        # import pdb
        # pdb.set_trace()

        in_template = False
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                print(f"Parsing line: {line}")

                # Split line into parts
                parts = line.split(maxsplit=2)
                key = parts[0]
                value = ' '.join(parts[1:]) if len(parts) > 1 else ''

                if key.startswith('@template'):
                    in_template = True
                    self.current_group = None
                    self.current_subgroup = self.templates.setdefault(value, {})
                    print(f"Template set: {value}, templates: {self.templates}")
                elif key.startswith('@use'):
                    in_template = False
                    if self.current_subgroup is not None:
                        self.current_subgroup.update(self.templates[value])
                        print(f"Applied template {value} to subgroup: {self.current_subgroup}")
                elif not in_template and len(parts) == 2 and not key.startswith('@') and ' ' not in value.strip():  # Group/subgroup
                    print("[A]")
                    group, subgroup = parts
                    print(f"xx parts {parts}")
                    print(f"self cfg {self.config}")
                    self.current_group = self.config.setdefault(group, {})
                    self.current_subgroup = self.current_group.setdefault(subgroup, {})
                    print(f"[A] Set group: {group}, subgroup: {subgroup}, config: {self.config}")
                elif value:  # Key-value pair
                    print("[B]")
                    if self.current_subgroup is not None:
                        print("[B1]")
                        self.current_subgroup[key] = self.parse_value(value)
                        print(f"[B2] Set {key} = {self.current_subgroup[key]} in subgroup: {self.current_subgroup}")
                    elif self.current_group is not None:
                        print("B3")
                        self.current_group[key] = self.parse_value(value)
                        print(f"B3 Set {key} = {self.current_group[key]} in group: {self.current_group}")
                    else:
                        self.config[key] = self.parse_value(value)
                        print(f"B4 Set {key} = {self.config[key]} in root: {self.config}")
                else:
                    in_template = False
                    self.current_group = self.config.setdefault(key, {})
                    self.current_subgroup = None
                    print(f"[C] Set group: {key}, config: {self.config}")

    def get_config(self):
        print("Final config:", self.config)
        return self.config


# Test
parser = SimplexParser()
parser.parse('config2.smpx')
print(json.dumps(parser.get_config(), indent=2))
