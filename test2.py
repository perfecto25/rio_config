#!/bin/python3

import re
import sys
from loguru import logger

def parse_config(file_content):
    
    # remove comments and emtpy lines
    cleaned_content = re.sub(r'^\s*#.*$(?:\n|$)', '', file_content, flags=re.MULTILINE)

    # Regex to match entire sections (e.g., [key1] followed by key-value pairs)
    section_pattern = r'\[([^\]]+)\]\s*((?:[^[\n]*\n*)*?)(?=\[|$|\Z)'
    # Regex for key-value pairs, excluding = inside quotes
    kv_pattern = r'^\s*([^=]+?)\s*=(?!(?:[^\'"]*(?:\'|")[^\'"]*?\1[^\'"]*)*$)\s*(.+?)\s*$'

    # Find all sections
    sections = re.findall(section_pattern, cleaned_content, re.MULTILINE)

    # Process sections into the desired structure
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
def parse_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return parse_config(content)

# Example usage with file content
file_content = """
[key1.key3]
sub1 = val1

[key2]
sub2 = val2"""



file = sys.argv[1]
# Parse the content
parsed_data = parse_file(file)
print(parsed_data)