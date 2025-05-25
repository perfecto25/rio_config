
import re
import sys
from loguru import logger
from .functions import create_nested_dict, \
    get_type, add_to_last_element, deep_merge_pipe, check_syntax


class Flex():

    def parse_config(self, file_content):

        # remove comments and emtpy lines
        cleaned_content = re.sub(r'^\s*#.*$(?:\n|$)', '', file_content, flags=re.MULTILINE)

        # check for parse errors
        check_syntax(cleaned_content)

        # Regex to match entire sections (e.g., [key1] followed by key-value pairs)
        section_pattern = r'\[([^\]]+)\]\s*((?:(?!\[[^\]]*\][^=]*=).*\n*)*?)(?=\[|$|\Z)'

        # Find all sections
        sections = re.findall(section_pattern, cleaned_content, re.MULTILINE)
        logger.info(f"sections = {sections}")

        ret = {}
        templates = {}
        
        logger.warning(sections)

        for key, content in sections:
            parsing_template = False
            keys_dict = {}
            logger.info(f">> 1 Section Key={key}, content={content}")

            if key.startswith('@template'):
                parsing_template = True
                template_name = key.split('@template')[1].strip()
                
                if not template_name in templates.keys():
                    templates[template_name] = {}
                    
            # check header key is quoted, strip quotes
            if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
                quote_char = key[:1]
                key = key.rstrip(quote_char).lstrip(quote_char)
                logger.warning(key)
                keys_dict[key] = {}
                logger.warning(keys_dict)
            # check for escape char
            if r"\." in key and not keys_dict:
                # generate keylist by replaceing escape dot with escape placeholder
                # to be able to split by actual dots
                key = key.replace(r'\.', '__flx__')
                logger.info(key)
                keylist = key.split('.')
                # regenerate keylist and re-substitute eschape placeholder with escape dot
                keylist = [item.replace('__flx__', '.') for item in keylist]
                logger.info(keylist)
                keys_dict = create_nested_dict(keylist)
            
            # generate dict with header subkeys ie [key1.key2.key3]
            if '.' in key and not keys_dict:
                keylist = key.split('.')
                keys_dict = create_nested_dict(keylist)

            if not keys_dict and not parsing_template:
                keys_dict[key] = {}

            logger.info(f"templates {templates}")
            # parse content and add back to ret[key]
            # pattern = r'^\s*(\w+)\s*=\s*(.*?)\s*(?=(?:\n\s*\w+\s*=|\Z))'
            # pattern = r'(\w+(?:\s+\w+)*)\s*=\s*(\w+(?:\s+\w+)*)'
            # pattern = r'((?:\w+\s+\w+|\w+)\s*=\s*(?:"[^"]*"|\w+))'
            # pattern = r'((?:\w+\s+\w+|\w+)\s*=\s*(?:"[^"]*"|\w+))'
            #pattern = r'^\s*([^=]+?)\s*=\s*(.*?)\s*(?=(?:\n\s*[^=]+\s*=|\Z))'
            #pattern = r'^\s*\[([^\]\[\\]+)\]\s*|\s*([^=]+?)\s*=\s*(\[.*?\](?=\s*(?:\n\s*[^=]+\s*=|\Z)))'
            pattern = r'^\s*\[([^\]\[\\]+)\]\s*$|^\s*([^=]+?)\s*=\s*((?:\"\"\".*?(?:\"\"\")|\[.*?\]|\S.*?)(?=\s*(?:\n\s*[^=]+\s*=|\n\s*\[|\Z)))'

            subsections = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            logger.info(f"subsections = {subsections}, keys_dict = {keys_dict}")
            
            sub_key = None
            use_list = []
            for match in subsections:
                logger.info(f"match = {match}, parsing_template={parsing_template}")
                if len(match) > 3:
                    logger.info(f"match3 {match[3]}")
                if match[0]: # section header
                    sub_key = match[0]
                elif match[1]:
                    sub_key = match[1]
                    sub_content = match[2]

                    # add template data to template dict
                    logger.info(f"templates {templates}, key={key}, subkey={sub_key}, subcontent={sub_content}")
                    
                    if parsing_template:                        
                        templates[template_name][sub_key] = get_type(sub_content)
                        continue
                        
                    logger.warning(f"key={sub_key}, value={sub_content}")
                    
                    if sub_key == "@use":

                        use_template_name = sub_content.strip()

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
                        continue

                    value = get_type(sub_content)
                    add_to_last_element(keys_dict, sub_key, value)
                    ret = deep_merge_pipe(ret, keys_dict)
        logger.success(f"templates= {templates}")
        return ret

    # Reading from a file

    def parse_file(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return self.parse_config(content)
