#!/usr/bin/python3
import sys
import json
from flex_markup import Flex


if __name__ == "__main__":

    
    file = sys.argv[1]
    flex = Flex()
    result = flex.parse_file(file)

#   
    print(result)
    #logger.debug(type(result))
    #print(json.dumps(result, ensure_ascii=False))
    