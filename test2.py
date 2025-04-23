import json
import re


def parse_config_file(filepath):
    result = {}
    current_section = None
    last_section_key = None
    section_path = []

    # Regex patterns
    section_pattern = re.compile(r'^\s*\[([^\]]*)\]\s*$')  # Matches [section] or [section.subsection]
    kv_pattern = re.compile(r'^\s*([^=]+?)\s*=\s*(.+?)\s*$')  # Matches key = value
    value_pattern = re.compile(r'^\s*([^=]+?)\s*$')  # Matches single value (no =)

    with open(filepath, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith(';') or line.startswith('#'):
                continue  # Skip empty lines and comments

            # Check for section header
            section_match = section_pattern.match(line)
            if section_match:
                section = section_match.group(1).strip()
                section_path = section.split('.')  # Split on . for nested sections
                last_section_key = section_path[-1]  # Track the last part (e.g., office)

                # Navigate to the section, creating nested dicts as needed
                current_section = result
                for i, part in enumerate(section_path):
                    if i < len(section_path) - 1:
                        # Intermediate section (e.g., company in company.office)
                        if part not in current_section:
                            current_section[part] = {}
                        current_section = current_section[part]
                    else:
                        # Final section (e.g., department or office)
                        if part not in current_section:
                            current_section[part] = {}
                        current_section = current_section[part]
                continue

            # Check for key-value pair
            kv_match = kv_pattern.match(line)
            if kv_match and current_section is not None:
                key = kv_match.group(1).strip()
                value = kv_match.group(2).strip()
                current_section[key] = value
                continue

            # Check for single value
            value_match = value_pattern.match(line)
            if value_match and current_section is not None and last_section_key:
                value = value_match.group(1).strip()
                # Assign single value to the last section key in the parent section
                parent_section = result
                for part in section_path[:-1]:
                    parent_section = parent_section[part]
                parent_section[last_section_key] = value
                # Reset current_section to parent to prevent further additions
                current_section = parent_section

    return result


# Example usage
filepath = 'f3.flx'  # Replace with your file path
config_dict = parse_config_file(filepath)
print(json.dumps(config_dict, indent=2))
