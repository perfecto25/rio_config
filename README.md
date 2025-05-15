# FLEX Markup Language

Flex is a markup language for use in common configuration scenarios.

It is similar to TOML in concept, but is unique in its approach to handling variables and configuration data

## Features
- no spacing requirements (ie, 2 spaces in YAML)
- braces not necessary (ie, json)
- can add comments
- clean and simple syntax to describe complex data structures
- ability to create template blocks for repeated options
- can natively ingest shell environment variables at runtime, including fallback values


## Usage

Flex can handle the following types

- strings
- ints
- floats
- booleans
- arrays



To create a basic key:value pair, you need a Header block (key)


    [Key]
    Value
  
  ie, 
  
    [Name]
    Joe 

    # equals  {"Name": "Joe"}

To created a nested hash

    [Parent Key]
    child key = child value

    [Employee]
    Name = Joe

    # equals {"Employee": {"Name": "Joe"}}

---

### Arrays

To create an array, pass a dash followed by a comma separated list of values

    [My List]
    - first, second, third

    # equals 
    {"My List": ["first", "second", "third"]}



--- 

### Templates

Templates allow you to reuse configuration data without copying and pasting the same data over and over.

for example, lets say you want to add some Company-specific data to every Employee

    [@template company]
    name = Initech
    address = 123 company drive
    phone = 200-301-4050

    [employees.Joe]
    @use company
    department = sales

    [employees.Bill]
    @use company
    department = engineering

    ## results in

    {
      "employees": {
        "Joe": {
          "name": "Initech",
          "address": "123 company drive",
          "phone": "200-301-4050",
          "department": "sales"
        },
        "Bill": {
          "name": "Initech",
          "address": "123 company drive",
          "phone": "200-301-4050",
          "department": "engineering"
        }
      }
    }

  

@use - use template (must match template name)

@template - create new template


    [@template red]
    from-red-template = this is a red value

    [@template blue]
    from-blue-template = this is a blue value

    [Flowers:species:rose]
    @use red
    roses = are red

    [Flowers:species:violet]
    @use blue
    violets = are blue

    [Flowers:species:tulip]
    @use red
    tulips = are red too!
    
    >>

    {
      "Flowers": {
        "species": {
          "rose": {
            "from-red-template": "this is a red value",
            "roses": "are red"
          },
          "violet": {
            "from-blue-template": "this is a blue value",
            "violets": "are blue"
          },
          "tulip": {
            "from-red-template": "this is a red value",
            "tulips": "are red too!"
          }
        }
      }
    }



deep hash

```
[check:filesystem:home]
name = "/home"

[check:filesystem:opt]
name = "/opt"

```

### Using environment variables

to process a shell environment variable, provide @env flag

    [database.credential]
    password = @env DB_PASSWORD

this will translate a shell variable $DB_PASSWORD

to pass a default fallback value if env variable isnt set, provide a default using the double pipe OR symbol

    [database.credential]
    password = @env DB_PASSWORD || abracadabra123


this will use "abracadabra123" as the fallback value


## Testing 

pip install pytest

shell> cd tests
shell> pytest -sv tests/run_tests.py

## TO DO:

