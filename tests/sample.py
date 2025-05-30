#!/usr/bin/python3
import sys
import json
from os.path import dirname, join, abspath

# import repo version of Rio, not pip-installed version
sys.path.insert(0, abspath(join(dirname(__file__), "..")))

from rio_config import Rio


if __name__ == "__main__":

    
    file = sys.argv[1]
    rio = Rio()
    result = rio.parse_file(file)

#   
    #print(result)
    #logger.debug(type(result))
    print(json.dumps(result, ensure_ascii=False))
    