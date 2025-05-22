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

You can also provide a value to the last key directly

    [first.second.third]
    value

    ## result
    
    {
      "first": {
        "second": {
          "third": "value"
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

---

### Arrays

To create an array, pass a dash followed by a comma separated list of values

    [My List]
    - first, second, third

    ## result 
    {
      "My List": [
        "first", 
        "second", 
        "third"
      ]
    }

Arrays can also be created using a multiline declaration starting with a dash

    [cars]
    names = -
      toyota,
      ferrari,
      chevy


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
    @use company
    department = sales

    [employees.Bill]
    @use company
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

