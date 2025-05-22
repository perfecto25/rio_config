import re
import os
import sys
from loguru import logger

logger.remove()
#logger.add(sys.stderr, level="CRITICAL")
logger.add(sys.stderr, level="DEBUG")

class Flex():

    def __init__(self): 
        self.data = None

    def parse_file(self, filepath):
        result = {}
        templates = {}  # Store template definitions
        current_section = None
        section_path = []
        current_template = None
        parsing_multiline_list = False
        multiline_list_key = None
        multiline_list_items = []
        parsing_multiline_comment = False
        multiline_comment_key = None
        multiline_comment_lines = []

        # Regex patterns
        section_pattern = re.compile(r'^\s*\[([^\]]*)\]\s*$')  # Matches [section] or [section.subsection]
        template_pattern = re.compile(r'^\s*\[@template\s+([^\]]*)\]\s*$')  # Matches [@template name]
        kv_pattern = re.compile(r'^\s*([^=]+?)\s*=\s*(.+?)\s*$')  # Matches key = value
        #kv_pattern = re.compile(r'^\s*([^=]+?)\s*=(?!(?:[^\'"]*(?:\'|")[^\'"]*?\1[^\'"]*)*$)\s*(.+?)\s*$') # matches key=value
        use_template_pattern = re.compile(r'^\s*@use\s+([^\s]+)\s*$')  # Matches @use template_name
        single_value_pattern = re.compile(r'^\s*([^=]+?)\s*$')  # Matches single value (no =)
        #env_var_pattern = re.compile(r'@env\s+([^\s]+)\s*\|\|?\s*\'([^\']*)\'')  # Matches @env ENV_VAR || 'fallback'
        env_var_pattern = re.compile(r'@env.*')
        single_line_list_pattern = re.compile(r'^\s*--+\s*([^=].*?)\s*$')  # Matches - item1,item2 or - "quoted item"
        multiline_list_start_pattern = re.compile(r'^\s*--+\s*$')  # Matches - (start of multi-line list)
        list_item_pattern = re.compile(r'(?:"([^"]*)"|([^",]+))')  # Matches quoted strings or non-quoted items
        multiline_comment_start_pattern = re.compile(r"^\s*([^=]+?)\s*=\s*'''\s*(.*)$")  # Matches key = """ with optional content
        multiline_comment_end_pattern = re.compile(r"^\s*(.*?)\s*'''\s*$")  # Matches optional content before """
        improper_list_warning = re.compile(r"=\s*-") # warns if list is provided with single dash, not double dash


        def remove_whitespace(text):
            """Removes all whitespace characters from a string."""
            return re.sub(r"\s+", "", text)

        def get_type(value):
            """checks if an integer, string, bool"""
            if not value:
                return
            ## String
            if value.startswith('"') or value.startswith("'"):
                value = value.rstrip('"').rstrip("'").lstrip('"').lstrip("' ")
                return str(value)
            
            ## Integer
            try:
                value = int(value)
                logger.success(value)
                return value
            except (TypeError, ValueError):
                pass

            ## Boolean
            if value in ["true", "True"]: 
                return True
            if value in ["false", "False"]:
                return False
            
            return value
            
        def substitute_env_vars(value):
            """Replace @env ENV_VAR || 'fallback' with environment variable or fallback."""
            if not value:
                return
            if not '@env' in value:
                return value

            fallback = None
            value = value.strip('@env').strip()
            
            if '||' in value:
                try:
                    fallback = value.split('||')[1].strip()
                    value = value.split('||')[0].strip()                
                except IndexError:
                    pass
            val = os.environ.get(value, fallback)
            if val:
                val.strip()
            return val
             
        def process_list_items(items, apply_env_vars=False):
            """Process list items, preserving quoted strings as single elements."""
            result = [] 
            for item in items:
                if item.startswith('"') and item.endswith('"'):
                    item_text = item[1:-1]  # Remove quotes
                    if item_text:
                        result.append(substitute_env_vars(item_text) if apply_env_vars else item_text)
                else:
                    matches = list_item_pattern.finditer(item)
                    for match in matches:
                        item_text = match.group(1) if match.group(1) is not None else match.group(2)
                        item_text = item_text.strip()
                        if item_text:
                            item_text = get_type(item_text)
                            result.append(substitute_env_vars(item_text) if apply_env_vars else item_text)
            return result

        def end_multiline_list():
            """Process and store multi-line list items, then reset state."""
            nonlocal parsing_multiline_list, multiline_list_key, multiline_list_items
            if multiline_list_items:
                processed_items = process_list_items(multiline_list_items)
                logger.debug(processed_items    )
                if current_template is not None:
                    current_template[multiline_list_key] = processed_items
                elif current_section is not None:
                    current_section[multiline_list_key] = processed_items
            parsing_multiline_list = False
            multiline_list_key = None
            multiline_list_items = []
            logger.info("END ML LIST --")

        def end_multiline_comment():    
            """Process and store multiline comment, then reset state."""
            nonlocal parsing_multiline_comment, multiline_comment_key, multiline_comment_lines
            if multiline_comment_lines:
                comment_text = ' '.join(line.strip() for line in multiline_comment_lines if line.strip())
                if current_template is not None:
                    current_template[multiline_comment_key] = comment_text
                elif current_section is not None:
                    current_section[multiline_comment_key] = comment_text
            parsing_multiline_comment = False
            multiline_comment_key = None
            multiline_comment_lines = []

        with open(filepath, 'r') as file:
            for line in file:
                
                ## Preserve all whitespace, remove only newline characters
                line = line.rstrip('\r\n')

                ## replace tabs w spaces
                line = line.replace('\t', ' ')

                ## skip empty lines, comments, space-only lines
                if not line or line.startswith(';') or line.startswith('#') or line.isspace():
                    continue
                
                logger.info(f"------------ line={line}<<")
                logger.info(line)
                logger.info(f"parsling ML list: {parsing_multiline_list}")
                logger.info(f"parsling ML comment: {parsing_multiline_comment}")

                ## clean up multiline comments convert to single quote troika
                line = line.replace('"""', "'''")

                ## if new K,V - reset multiline data
                kv_match = kv_pattern.match(line)
                if kv_match:
                    parsing_multiline_comment = False
                    parsing_multiline_list = False
                    logger.debug("KV MATCH early")

                ## Handle multiline comment
                if parsing_multiline_comment:
                    end_comment_match = multiline_comment_end_pattern.match(line)
                    if end_comment_match:
                        ## Capture content before """ on the closing line
                        last_line_content = end_comment_match.group(1).strip()
                        if last_line_content:
                            multiline_comment_lines.append(last_line_content)                    
                        end_multiline_comment()
                        continue
                    elif section_pattern.match(line) or template_pattern.match(line):
                        ## Force end comment if a new section starts
                        end_multiline_comment()
                        ## Reprocess the line as a section header
                    else:
                        multiline_comment_lines.append(line)
                        continue

                ## Warn on improper List definition
                if improper_list_warning.match(line):
                    print(f"WARNING: improper list format: {line}")

                ## Handle multi-line list items
                if parsing_multiline_list:
                    #line = line.replace('=', '__x__')
                    logger.error(line)
                    list_item_matches = list(list_item_pattern.finditer(line))
                    logger.info(f"list_item_matches: {list_item_matches}")
                    if list_item_matches and not any(p.match(line) for p in [
                        section_pattern, template_pattern, kv_pattern, use_template_pattern, single_line_list_pattern,
                        multiline_comment_start_pattern
                    ]):
                        items = [match.group(1) if match.group(1) is not None else match.group(2) for match in list_item_matches]
                        multiline_list_items.extend([i.strip() for i in items if i.strip()])
                        logger.info(multiline_list_items)
                        continue
                    # handle multiline list items that have equal sign and quotes, ie '=value'
                    elif line.count('=') > 0 and not '=--' in remove_whitespace(line):
                       logger.info(line.strip())
                       logger.info(f"XX multiline list items {multiline_list_items} + {line}")
                       multiline_list_items.append(line)
                       continue
                    else:
                        end_multiline_list()

                ## Check for template definition
                template_match = template_pattern.match(line)
                if template_match:
                    template_name = template_match.group(1).strip()
                    templates[template_name] = {}
                    current_template = templates[template_name]
                    current_section = None
                    section_path = []
                    continue

                # Check for section header
                section_match = section_pattern.match(line)
                
                if section_match:
                    section = section_match.group(1).strip()
                    escaped = False
                    ## check if escape char is in key header
                    if r"\." in section:
                        section = section.replace(r'\.', '__flx_markup_escape__')
                        escaped = True


                    section_path = section.split('.')
                    
                    ## reassamble escaped notation
                    if escaped:
                        for path in section_path:
                            if '__flx_markup_escape__' in path:
                                index = section_path.index(path)
                                path = path.replace('__flx_markup_escape__', '.')
                                section_path[index] = path

                    current_template = None
                    current_section = result
                    for part in section_path[:-1]:
                        if part not in current_section:
                            current_section[part] = {}
                        elif not isinstance(current_section[part], dict):
                            current_section[part] = {'value': current_section[part]}
                        current_section = current_section[part]

                    last_key = section_path[-1]
                    if last_key not in current_section:
                        current_section[last_key] = {}
                    elif not isinstance(current_section[last_key], dict):
                        current_section[last_key] = {'value': current_section[last_key]}
                    current_section = current_section[last_key]
                    continue

                # Check for multiline comment start
                comment_start_match = multiline_comment_start_pattern.match(line)
                if comment_start_match:
                    parsing_multiline_comment = True
                    multiline_comment_key = comment_start_match.group(1).strip()
                    multiline_comment_lines = []
                    # Capture any content after """ on the same line
                    first_line_content = comment_start_match.group(2).strip()
                    if first_line_content:
                        multiline_comment_lines.append(first_line_content)
                    continue

                # Check for key-value pair (including single-line lists)
                logger.warning(line)
                if parsing_multiline_list:
                    logger.debug("PARSING ML list")
                kv_match = kv_pattern.match(line)
                if kv_match:
                    logger.debug(f"KV mathch: {line}")
                    key = kv_match.group(1).strip()
                    value = get_type(kv_match.group(2).strip())
                    logger.debug(f"{key} {value}")
                    
                    list_match = single_line_list_pattern.match(str(value))
                    logger.debug(list_match)
                    if list_match:
                        items = [list_match.group(1)]
                        logger.debug(items)
                        processed_items = process_list_items(items)
                        logger.info(processed_items)
                        if current_template is not None:
                            current_template[key] = processed_items
                        elif current_section is not None:
                            logger.info('curr_sec')
                            current_section[key] = processed_items
                            logger.info(current_section[key])
                    elif multiline_list_start_pattern.match(str(value)):
                        logger.info('multiline list start pattern')
                        logger.info(f"current_section[key] = {current_section   }")
                        parsing_multiline_list = True
                        multiline_list_key = key
                        multiline_list_items = []

                    elif env_var_pattern.match(str(value)):
                        value = substitute_env_vars(value)
                        if current_template is not None:
                            current_template[key] = value
                        elif current_section is not None:
                            current_section[key] = value
                    else:
                        if current_template is not None:
                            current_template[key] = value
                        elif current_section is not None:
                            current_section[key] = value
                    logger.info(f"final value {current_section}")
                    continue
                    logger.info("after continue")

                # Check for @use template
                use_template_match = use_template_pattern.match(line)
                if use_template_match and current_section is not None:
                    template_name = use_template_match.group(1).strip()
                    if template_name in templates:
                        for key, value in templates[template_name].items():
                            if isinstance(value, list):
                                current_section[key] = value
                            else:
                                current_section[key] = substitute_env_vars(value)
                    else:
                        print(f"Warning: Template '{template_name}' not found")
                    continue

                # Check for single value or section-level list
                logger.debug(line)
                list_match = single_line_list_pattern.match(line)
                logger.debug(list_match)
                
                if list_match and current_section is not None and section_path:
                    logger.warning("XX")
                    items = [list_match.group(1)]
                    processed_items = process_list_items(items)
                    parent_section = result
                    for part in section_path[:-1]:
                        parent_section = parent_section[part]
                    parent_section[section_path[-1]] = processed_items
                    current_section = parent_section
                    continue

                # Check for single value
                value_match = single_value_pattern.match(line)
                if value_match and current_section is not None and section_path:
                    value = value_match.group(1).strip()
                    value = get_type(value)
                    logger.warning(value)
                    if '@env' in line:
                        value = get_type(substitute_env_vars(value))
                    parent_section = result
                    
                    for part in section_path[:-1]:
                        parent_section = parent_section[part]
                    parent_section[section_path[-1]] = value
                    current_section = parent_section

                    continue

            # Handle any remaining multiline list or comment at EOF
            if parsing_multiline_list:
                end_multiline_list()
            if parsing_multiline_comment:
                print("Warning: Unclosed multiline comment at EOF")
                end_multiline_comment()
        logger.info(result)
        return result

    ## TO DO
#    def convert_from_yaml(self, file_path):
#        """ open YAML file and convert to a FLEX fornat, return result"""
