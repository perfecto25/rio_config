d = {'k1': {'k2': {'k3': {}}}}

current = d
parent = None
last_key = None

while current and isinstance(next(iter(current.values())), dict):
    parent = current
    last_key = next(iter(current.keys()))
    current = next(iter(current.values()))

# Set the value at the last key
if parent is not None and last_key is not None:
    parent[last_key] = 'abc'

print(d)