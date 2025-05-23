
import re
import sys
from loguru import logger
from .functions import parse_section, create_nested_dict

class Flex():

    def parse_config(self, file_content):

        # remove comments and emtpy lines
        cleaned_content = re.sub(r'^\s*#.*$(?:\n|$)', '', file_content, flags=re.MULTILINE)

        # Regex to match entire sections (e.g., [key1] followed by key-value pairs)
        section_pattern = r'\[([^\]]+)\]\s*((?:(?!\[[^\]]*\][^=]*=).*\n*)*?)(?=\[|$|\Z)'

        # Find all sections
        sections = re.findall(section_pattern, cleaned_content, re.MULTILINE)

        # Generate sections
        all_sections = []
        logger.warning(sections)

        for section, content in sections:

            
            all_sections.append((section, content))
        logger.info(f"all_sections {all_sections}")
        
        # parse each section
        ret = {}


           # check header key is quoted, strip quotes
        if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
            quote_char = key[:1]
            key = key.rstrip(quote_char).lstrip(quote_char)
            section_dict[key] = {}
    
        # check for escape char
        if r"\." in key and not ret:
            # generate keylist by replaceing escape dot with escape placeholder
            # to be able to split by actual dots
            key = key.replace(r'\.', '__flx__')
            keylist = key.split('.')

        # regenerate keylist and re-substitute eschape placeholder with escape dot
        keylist = [item.replace('__flx__', '.') for item in keylist]
        section_dict = create_nested_dict(keylist)

        # generate dict with header subkeys ie [key1.key2.key3]
        if '.' in key and not section_dict:
            keylist = key.split('.')
            section_dict = create_nested_dict(keylist)

        for section in all_sections:
            logger.info(section)
            try:
                key = section[0]
                val = section[1]
            except (IndexError, TypeError) as error:
                print(f"unable to process Flex config: {error}")
                sys.exit()

            # if header key in form of [key.key2.key3] etc
            ret = parse_section(key, val, ret)


            # if key not in ret:
            #     ret[key] = {}

        return ret


    
    # Reading from a file
    def parse_file(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return self.parse_config(content)