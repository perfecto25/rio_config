import re
from loguru import logger

def parse_sections(file_path):
    # Initialize result to store sections
    sections = {}
    current_section = None
    current_lines = []

    # Regular expression to match section headers like [section:one], [newsection], etc.
    section_pattern = re.compile(r'^\[([^\]]*)\]')

    # Read the file
    with open(file_path, 'r') as file:
        for line in file:
            logger.success(line)
            line = line.strip()  # Remove leading/trailing whitespace
            if not line or line.startswith('#'):
                continue  # Skip empty lines or comments

            # Check if the line is a section header
            match = section_pattern.match(line)
            if match:
                # If there's a previous section, save it
                if current_section is not None:
                    
                    logger.debug(f"current_section is not none: {current_section}")
                    sections[current_section] = current_lines
                    current_section = match.group(1)
                    continue
                # Start a new section
                logger.debug(f"current_Section is NONE")
                current_section = match.group(1)
                current_lines = []
            else:
                # Add line to the current section
                if current_section is not None:

                    current_lines.append(line)
            
        # Save the last section
        logger.info(f"current_section: {current_section}")
        logger.info(f"current_lines: {current_lines}")
        if current_section is not None:
            sections[current_section] = current_lines

    return sections

# Example usage
file_path = 'f3.flx'  # Replace with your file path
sections = parse_sections(file_path)
logger.warning(sections)
ret = {}
templates = {}

print(sections)
# Print the parsed sections
for section, lines in sections.items():
    parsing_template = False    
    # check if template section
    if "@template" in section:
        template_name = section.split("@template")[1].strip("[]").strip()
        parsing_template = True
        templates[template_name] = {}
    
    # check if section is single key=val
    if len(lines) == 1 and "=" not in lines[0] and not parsing_template:
        ret[section] = lines[0]
        continue

    if section not in ret.keys() and not parsing_template:
        ret[section] = {}
    

    print(f"lines: {lines}")
    
    print(f"Section: {section}")
    for line in lines:
        logger.info(lines)
        # get key, val
        new_key, new_val = [part.strip() for part in line.split('=', 1)]
        logger.debug(f"{new_key}:{new_val}" )
        
        if parsing_template:
            templates[template_name][new_key] = new_val
            continue
        ret[section][new_key] = new_val
         
        print(f"  {line}")

print(ret)