#!/usr/bin/python3
import os
import json
from flex_markup import Flex
from loguru import logger

if __name__ == "__main__":
    # pdb.set_trace()
    import sys
    f = sys.argv[1]
    with open(f) as file:
        data = file.read()

    os.environ['DOMAIN'] = 'example.com'
    os.environ['HOME'] = '/home/user'
    try:
        flex = Flex()
        result = flex.parse(data)

#        result = parse_scm(data)
    except (IndexError, TypeError) as err:
        print("[ERROR] unable to parse config file")
        raise Exception(str(err))

 #   print(result["check"]["filesystem"])
    logger.debug(type(result))
    print(json.dumps(result, ensure_ascii=False))
 #   print(json.dumps(result, indent=2))
