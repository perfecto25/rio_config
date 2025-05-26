# FLEX Markup Language

Flex is a markup language for use in common configuration scenarios.

It is similar to TOML and YAML in concept, but is unique in its approach to handling variables and configuration data

## Features
- no spacing requirements (ie, 2 spaces in YAML)
- braces not necessary (ie, json)
- can add comments
- clean and simple syntax to describe complex data structures
- ability to create template blocks for repeated options
- can natively ingest shell environment variables at runtime, including fallback values
- ability to created nested hashes without excessive notation and spacing



## Usage

Flex can handle the following types

- strings
- hashes
- ints
- floats
- booleans
- arrays



To create a basic key:value pair, you need a Header block (top key or Parent key)


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

To create a deep hash structure, add a key block declaration of all top keys and a final value, separated by a dot

Flex will create all parent subkeys along the path

    [first.second.third]
    fourth = value

    ## result

    {
    "first": {
      "second": {
        "third": {
          "fourth": "value"
          }
        }
      }
    }


if the top level key has dot in its name, you can escape parsing it with an escape character '\\.'

    [first.second\.level.third]
    value

    ## result

    {
      "first": {
        "second.level": {
          "third": "value"
        }
      }
    }

If the Parent key has dots in the name and you want to keep it as single key, double quote the parent key

    ["parent.key.separated.by.dot"]
    subkey = value

    ## result

    {
      "parent.key.separated.by.dot": {
        "subkey": "value"
      }
    }


---

### Arrays

To create an array, declare it using brackets, with each element separated by a comma

    [My List]
    subkey = [first, second, third]

    ## result 
    {
      "My List": {
        "subkey": [
          "first",
          "second",
          "third"
        ]
      }
    }

Arrays can also be created using a multiline declaration within a bracket pair

    [cars]
    names = [
      toyota,
      ferrari,
      chevy
    ]


    ## result
    {
      "cars": {
        "names": [
          "toyota",
          "ferrari",
          "chevy"
        ]
      }
    }

---

### Strings, Ints, Booleans, Floats

Flex will evaluate each value for its type, ie strings, ints, floats, booleans

By default, all values are strings, unless its a raw integer. To treat an integer as a string, double quote it

    [variables]
    string = this is a string
    real int = 12345
    stringified int = "12345"
    boolean true = True
    boolean false = False
    boolean strinfigied = "True"
    float = 2.34596

    ## result

    {
      "variables": {
        "string": "this is a string",
        "real int": 12345,
        "stringified int": "12345",
        "boolean true": true,
        "boolean false": false,
        "boolean strinfigied": "True",
        "float": 2.34596
      }
    }

--- 

### Templates

Templates allow you to reuse configuration data without copying and pasting the same data over and over.

Templates are created by using the @template keyword

[**@template** TemplateName] declares a new template, followed by template variables

**@use** keyword then instructs the key block to use the variables from the given template, ie

    @use myTemplate


for example, lets say you want to add some Company-specific data to every Employee

    [@template company]
    name = Initech
    address = 123 company drive
    phone = 200-301-4050

    [employees.Joe]
    @use = company
    department = sales

    [employees.Bill]
    @use = company
    department = engineering

    ## result:

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

to overwrite a template's variable with a custom value, simply provide a new variable with same name

for example, if I want Bill's phone number to be 111-111-1111 instead of the phone number from the template, I can add a new variable called "phone" which will override the previous value coming from the template

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
    phone = 111-111-1111  

    ## result 
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
          "phone": "111-111-1111",
          "department": "engineering"
        }
      }
    }

---

### Environment Variables

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

