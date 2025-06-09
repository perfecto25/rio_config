
import re
from .functions import create_nested_dict, \
    get_type, add_to_last_element, deep_merge_pipe, check_syntax, get_env_var, remove_use_keys, set_last_key, \
    remove_comments

class Rio():
    def parse_config(self, file_content):
        
        ret = {}
        templates = {}
        
        # remove comments and empty lines
        cleaned_content = re.sub(r'^\s*#.*$(?:\n|$)', '', file_content, flags=re.MULTILINE)
        # check for parse errors
        cleaned_content = check_syntax(cleaned_content)
        capture = re.compile(r'^(?P<key>(["\'].*?["\'])|(@?(?:\\.|[a-zA-Z0-9_. ])+)):\s*$', re.MULTILINE)
        matches = list(capture.finditer(cleaned_content))
        sections = []

        for i, match in enumerate(matches):
            
            key = match.group('key')
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned_content)
            content = cleaned_content[start:end].strip()
            sections.append((key, content))

        for key, content in sections:
            parsing_template = False
            keys_dict = {}
            if key.startswith('@template'):
                parsing_template = True
                template_name = key.split('@template')[1].strip()

                if template_name not in templates.keys():
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
            
            # simple key=val
            if not subsections:
                content = remove_comments(content)
                value = get_type(content)
                # check for comments on lines end
                set_last_key(keys_dict, value)
                ret = deep_merge_pipe(ret, keys_dict)
                continue

            for match in subsections:
                # direct simple list
                if match[0]:
                    if "," in match[0]:
                        value = match[0].split(",")
                        value = [get_type(x.strip()) for x in value if x]
                        set_last_key(keys_dict, value)
                        ret = deep_merge_pipe(ret, keys_dict)
                        continue
                subkey = match[1]
                subval = match[2]
                
                # check if nested subkey, ie  key1.key2.key3 = value
                if not subkey.startswith('"') and not subkey.startswith("'") and '.' in subkey:
                    keylist = f"{key}.{subkey}".strip().split('.')
                    temp_dict = create_nested_dict(keylist)
                    original_keys_dict = keys_dict
                    set_last_key(temp_dict, get_type(subval))
                    keys_dict = deep_merge_pipe(keys_dict, temp_dict)
                    ret = deep_merge_pipe(ret, keys_dict)
                    keys_dict = original_keys_dict
                    continue
                
                if parsing_template:
                    templates[template_name][subkey] = get_type(subval)
                    continue
                if subkey == "@use":
                    use_template_name = subval.strip()
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
                
                if "@env" in subval:
                    value = get_env_var(subval)
                else:
                    value = remove_comments(subval)
                    value = get_type(value)
                add_to_last_element(keys_dict, subkey.rstrip('"').lstrip('"').rstrip("'").lstrip("'"), value)
                ret = deep_merge_pipe(ret, keys_dict)

        return remove_use_keys(ret)

    # Reading from a file
    def parse_file(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return self.parse_config(content)
