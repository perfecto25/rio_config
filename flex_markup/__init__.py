
import re
import sys
from loguru import logger


class Flex():

    def parse_config(self, file_content):

        # remove comments and emtpy lines
        cleaned_content = re.sub(r'^\s*#.*$(?:\n|$)', '', file_content, flags=re.MULTILINE)

        # Regex to match entire sections (e.g., [key1] followed by key-value pairs)
        section_pattern = r'\[([^\]]+)\]\s*((?:[^[\n]*\n*)*?)(?=\[|$|\Z)'
        # Regex for key-value pairs, excluding = inside quotes
        kv_pattern = r'^\s*([^=]+?)\s*=(?!(?:[^\'"]*(?:\'|")[^\'"]*?\1[^\'"]*)*$)\s*(.+?)\s*$'

        # Find all sections
        sections = re.findall(section_pattern, cleaned_content, re.MULTILINE)

        # Generate sections
        result = []

        for section, content in sections:
            result.append((section, content))
    

        return result
    # result = [
    #     {
    #         section.strip(): {
    #             match.group(1).strip(): match.group(2).strip()
    #             for match in re.finditer(kv_pattern, content, re.MULTILINE)
    #             if match.group(0).strip()  # Skip empty matches
    #         }
    #     }
    #     for section, content in sections
    #     if section.strip()  # Ensure section name is not empty
    # ]

    
    # Reading from a file
    def parse_file(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return self.parse_config(content)