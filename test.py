#!/usr/bin/python3


class Groml():
    def __init__(self):
        self.config = {}
        self.templates = {}


    def parse(self, filename):
        data = {}
        with open(filename, 'r') as f:
            content = f.read()
            for block in content.split("\n\n"):
                print(f"BLOCK {block}")
                for line in block.split("\n"):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    print(f"LINE {line}")
                    # Split line into parts
                    parts = line.split(maxsplit=2)
                    key = parts[0]
                    value = ' '.join(parts[1:]) if len(parts) > 1 else ''
                    print(f"parts {parts}")
                    print(f"key {key}")
                    
                print("----")


parser = Groml()
data = parser.parse("config.v1")
print(data)