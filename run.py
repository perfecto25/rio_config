#!/usr/bin/python3
import os
import json
from fml import Fml
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
        fml = Fml()
        result = fml.parse(data)

#        result = parse_scm(data)
    except (IndexError, TypeError) as err:
        print("[ERROR] unable to parse config file")
        raise Exception(str(err))
    
    logger.debug(result)
    logger.warning(result["check"]["fs"])
 #   print(result["check"]["filesystem"])
    print(json.dumps(result))
 #   print(json.dumps(result, indent=2))
