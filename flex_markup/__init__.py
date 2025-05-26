
import re
from loguru import logger
from .functions import create_nested_dict, \
    get_type, add_to_last_element, deep_merge_pipe, check_syntax, get_env_var, remove_use_keys


class Flex():
    def parse_config(self, file_content):

        # remove comments and emtpy lines
        cleaned_content = re.sub(r'^\s*#.*$(?:\n|$)', '', file_content, flags=re.MULTILINE)

        # check for parse errors
        cleaned_content = check_syntax(cleaned_content)

        # Regex to match entire sections (e.g., [key1] followed by key-value pairs)
        section_pattern = r'\[([^\]]+)\]\s*((?:(?!\[[^\]]*\][^=]*=).*\n*)*?)(?=\[|$|\Z)'

        # Find all sections
        sections = re.findall(section_pattern, cleaned_content, re.MULTILINE)

        ret = {}
        templates = {}

        for key, content in sections:
            parsing_template = False
            keys_dict = {}

            if key.startswith('@template'):
                parsing_template = True
                template_name = key.split('@template')[1].strip()

                if not template_name in templates.keys():
                    templates[template_name] = {}

            # check header key is quoted, strip quotes
            if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
                quote_char = key[:1]
                key = key.rstrip(quote_char).lstrip(quote_char)
                keys_dict[key] = {}
            # check for escape char
            if r"\." in key and not keys_dict:
                # generate keylist by replaceing escape dot with escape placeholder
                # to be able to split by actual dots
                key = key.replace(r'\.', '__flx__')
                keylist = key.split('.')
                # regenerate keylist and re-substitute eschape placeholder with escape dot
                keylist = [item.replace('__flx__', '.') for item in keylist]
                keys_dict = create_nested_dict(keylist)

            # generate dict with header subkeys ie [key1.key2.key3]
            if '.' in key and not keys_dict:
                keylist = key.split('.')
                keys_dict = create_nested_dict(keylist)

            if not keys_dict and not parsing_template:
                keys_dict[key] = {}

            pattern = r'^\s*\[([^\]\[\\]+)\]\s*$|^\s*([^=]+?)\s*=\s*((?:\"\"\".*?(?:\"\"\")|\[.*?\]|\S.*?)(?=\s*(?:\n\s*[^=]+\s*=|\n\s*\[|\Z)))'
            subsections = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            sub_key = None
            for match in subsections:
                if match[0]:  # section header
                    sub_key = match[0]
                elif match[1]:
                    sub_key = match[1]
                    sub_content = match[2]

                    # add template data to template dict
                    if parsing_template:
                        templates[template_name][sub_key] = get_type(sub_content)
                        continue

                    if sub_key == "@use":
                        use_template_name = sub_content.strip()

                        if use_template_name not in templates.keys():
                            raise Exception(f"template not found: {use_template_name}")

                        if use_template_name in templates.keys():
                            template_dict = {}

                            # generate temporary template dict and merge into keys_dict
                            if '.' in key:
                                keylist = key.split('.')
                                template_dict = create_nested_dict(keylist)
                            else:
                                template_dict[key] = {}

                            for k, v in templates[use_template_name].items():
                                add_to_last_element(keys_dict, k, v)
                    else:
                        value = get_type(sub_content)
                        add_to_last_element(keys_dict, sub_key, value)
                        ret = deep_merge_pipe(ret, keys_dict)

                if "@env" in sub_content:
                    value = get_env_var(sub_content)
                else:
                    value = get_type(sub_content)
                add_to_last_element(keys_dict, sub_key, value)
                ret = deep_merge_pipe(ret, keys_dict)

        # clean return dict of any @use key, values
        ret = remove_use_keys(ret)

        return ret

    # Reading from a file

    def parse_file(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return self.parse_config(content)
