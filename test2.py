import re
import os

def parse_config_file(filepath):
    result = {}
    templates = {}  # Store template definitions
    current_section = None
    section_path = []
    current_template = None

    # Regex patterns
    section_pattern = re.compile(r'^\s*\[([^\]]*)\]\s*$')  # Matches [section] or [section.subsection]
    template_pattern = re.compile(r'^\s*\[@template\s+([^\]]*)\]\s*$')  # Matches [@template name]
    kv_pattern = re.compile(r'^\s*([^=]+?)\s*=\s*(.+?)\s*$')  # Matches key = value
    use_template_pattern = re.compile(r'^\s*@use\s+([^\s]+)\s*$')  # Matches @use template_name
    value_pattern = re.compile(r'^\s*([^=]+?)\s*$')  # Matches single value (no =)
    env_var_pattern = re.compile(r'@env\s+([^\s]+)\s*\|\|\s*\'([^\']*)\'')  # Matches @env ENV_VAR || 'fallback'

    def substitute_env_vars(value):
        """Replace @env ENV_VAR || 'fallback' with environment variable or fallback."""
        def replace_match(match):
            env_var = match.group(1).strip()
            fallback = match.group(2)
            return os.getenv(env_var, fallback)
        
        return env_var_pattern.sub(replace_match, value)

    with open(filepath, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith(';') or line.startswith('#'):
                continue  # Skip empty lines and comments

            # Check for template definition
            template_match = template_pattern.match(line)
            if template_match:
                template_name = template_match.group(1).strip()
                templates[template_name] = {}  # Initialize template
                current_template = templates[template_name]
                current_section = None  # Reset current section
                section_path = []
                continue

            # Check for section header
            section_match = section_pattern.match(line)
            if section_match:
                section = section_match.group(1).strip()
                section_path = section.split('.')  # Split on . for nested sections
                current_template = None  # Reset template context

                # Navigate to the parent section
                current_section = result
                for part in section_path[:-1]:
                    if part not in current_section:
                        current_section[part] = {}
                    elif not isinstance(current_section[part], dict):
                        # Convert string to dict if it was a single value
                        current_section[part] = {'value': current_section[part]}
                    current_section = current_section[part]

                # Initialize or reuse the final section
                last_key = section_path[-1]
                if last_key not in current_section:
                    current_section[last_key] = {}
                elif not isinstance(current_section[last_key], dict):
                    # Convert string to dict if it was a single value
                    current_section[last_key] = {'value': current_section[last_key]}
                current_section = current_section[last_key]
                continue

            # Check for key-value pair
            kv_match = kv_pattern.match(line)
            if kv_match:
                key = kv_match.group(1).strip()
                value = kv_match.group(2).strip()
                # Substitute environment variables in the value
                value = substitute_env_vars(value)
                if current_template is not None:
                    # Add to template
                    current_template[key] = value
                elif current_section is not None:
                    # Add to current section
                    current_section[key] = value
                continue

            # Check for @use template
            use_template_match = use_template_pattern.match(line)
            if use_template_match and current_section is not None:
                template_name = use_template_match.group(1).strip()
                if template_name in templates:
                    # Apply template key-value pairs to current section
                    for key, value in templates[template_name].items():
                        # Substitute env vars in template values
                        value = substitute_env_vars(value)
                        current_section[key] = value
                else:
                    print(f"Warning: Template '{template_name}' not found")
                continue

            # Check for single value
            value_match = value_pattern.match(line)
            if value_match and current_section is not None and section_path:
                value = value_match.group(1).strip()
                # Substitute environment variables in the value
                value = substitute_env_vars(value)
                # Assign single value to the last section key in the parent section
                parent_section = result
                for part in section_path[:-1]:
                    parent_section = parent_section[part]
                parent_section[section_path[-1]] = value
                # Update current_section to reflect the parent
                current_section = parent_section
                continue

    return result

# Example usage
filepath = 'f3.flx'  # Replace with your file path
config_dict = parse_config_file(filepath)
import json
print(json.dumps(config_dict, indent=2))