# Rio Configuration Parser


<img src="./img/logo.png">

Rio is a configuration parser for use in common configuration scenarios.

It is similar to TOML and YAML in concept, but is unique in its approach to handling variables and configuration data, with focus on simplicity of declaration of complex data structures.

## Features
- no spacing requirements (ie, 2 spaces in YAML)
- braces not necessary (ie, json)
- can add comments inside configuration
- clean and simple syntax to describe complex data structures
- ability to create template blocks for repeated options
- can natively ingest shell environment variables at runtime, including fallback values
- ability to created nested hashes without excessive notation and spacing


---

## Usage

Rio can handle the following types

- strings
- hashes
- ints
- floats
- booleans
- arrays


To create a basic key:value pair, you need a Header block (top key or Parent key) which is denoted by colon at end


    Key:
    Value
  
  ie, 
  
    Name:
    "Joe" 

    # equals  {"Name": "Joe"}

To created a nested hash

    Parent Key:
    child key = child value

    Employee:
    Name = "Joe"

    # equals {"Employee": {"Name": "Joe"}}

double quoting non numeric values is recommended to avoid ambiguous value declaration

---

### Basic Dictionary/Hash

To create a deep hash structure, add a key block declaration of all top keys and a final value, separated by a dot

Rio will create all parent subkeys along the path

    first.second.third:
      fourth = value

  result

    {
    "first": {
      "second": {
        "third": {
          "fourth": "value"
          }
        }
      }
    }

double spacing the subkey=value is not mandatory but is recommended for readability, ie

    first.second.third:
      fourth = value

---

### Escape Character

if the top level key has dot in its name, you can escape parsing it with an escape character '\\.'

    first.second\.level.third:
      value

  result

    {
      "first": {
        "second.level": {
          "third": "value"
        }
      }
    }

---

### Single Key
If the Parent key has dots in the name and you want to keep it as single key, double quote the parent key

    "parent.key.separated.by.dot":
    subkey = value

  result

    {
      "parent.key.separated.by.dot": {
        "subkey": "value"
      }
    }


---

### Arrays

To create an array, declare it using brackets, with each element separated by a comma

    My List:
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

    cars:
      names = [
        toyota,
        ferrari,
        chevy
      ]


  result

    {
      "cars": {
        "names": [
          "toyota",
          "ferrari",
          "chevy"
        ]
      }
    }

you can also create an array without a subkey,

    my array:
      ['a', 'b', 'c']

result

    {
      "my array": [
        "a",
        "b",
        "c"
      ]
    }


---

### Child nested subkeys

With Rio you can also create nested subkeys underneath your parent key, by placing a dot in the subkey declaration

    config.nginx:
      cache.size = 200
      cache.limit = 190
      cache.clean.size = 5

result 

    {
      "config": {
        "nginx": {
          "cache": {
            "size": 200,
            "limit": 190,
            "clean": {
              "size": 5
            }
          }
        }
      }
    }

To treat a child subkey with dots a single key, wrap it in quotes

    config.nginx:
      cache.size = 200
      cache.limit = 190
      "cache.clean.size" = 5


---

### Strings, Ints, Booleans, Floats

Rio will evaluate each value for its type, ie strings, ints, floats, booleans

By default, all values are strings, unless its a raw integer. To treat an integer as a string, double quote it

    variables:
      string = this is a string
      real int = 12345
      stringified int = "12345"
      boolean true = True
      boolean false = False
      boolean strinfigied = "True"
      float = 2.34596

  result

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

**@template TemplateName:** declares a new template, followed by template variables

**@use** keyword then instructs the key block to use the variables from the given template, ie

    @use = myTemplate


for example, lets say you want to add some Company-specific data to every Employee 

(note: double spacing the subkeys is not mandatory but recommended, purely for visual clarity)

    @template company:
      name = "Initech"
      address = "123 company drive"
      phone = "200-301-4050"

    employees.Joe:
      @use = company
      department = "sales"

    employees.Bill:
      @use = company
      department = "engineering"

  result:

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

for example, if you want Bill's phone number to be 111-111-1111 instead of the phone number from the template, you can add a new variable called "phone" which will override the previous value coming from the template

    @template company:
      name = Initech
      address = "123 company drive"
      phone = "200-301-4050"

    employees.Joe:
      @use = company
      department = "sales"

    employees.Bill:
      @use = company
      department = "engineering"
      phone = "111-111-1111"

  result 

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

You can also combine multiple templates in one config block

    @template evens:
      even_numbers = [2,4,6,8]

    @template odds:
      odd_numbers = [1,3,5,7]

    @template words:
      hello = world
      bunch of words = [
        sunflower,
        gunpowder,
        beer
      ]

    combined stuff:
      @use = evens
      @use = odds
      @use = words

result will contain all your template variables

    {
      "combined stuff": {
        "even_numbers": [
          2,
          4,
          6,
          8
        ],
        "odd_numbers": [
          1,
          3,
          5,
          7
        ],
        "hello": "world",
        "bunch of words": [
          "sunflower",
          "gunpowder",
          "beer"
        ]
      }
    }


---

### Multiline Comments

comments or text spanning multiple lines can be written using the single quote troika

    mycomment:
      comment = '''
      this 
      is 
      a comment
      that    spans

      many

      lines
      '''

  result

    {
    "mycomment": {
      "comment": "\nthis \nis \na comment\nthat    spans\n\nmany\n\nlines\n"
      }
    }



---

### Environment Variables

to process a shell environment variable, provide @env flag

    database.credential:
      password = @env DB_PASSWORD

this will translate a shell variable $DB_PASSWORD

if the variable is not set, the value will be NULL

to pass a default fallback value if env variable isnt set, provide a default using the double pipe OR symbol



    database.credential:
      password = @env DB_PASSWORD || abracadabra123


result

    {
    "database": {
      "credential": {
        "password": "abracadabra123"
        }
      }
    }

  

```bash
export DB_PASSWORD="cheese-is-yummy991"
```



    {
    "database": {
      "credential": {
        "password": "cheese-is-yummy991"
        }
      }
    }


---

### Comments

Comments within the configuration data can be added with # symbol

    # this is a comment
    key:
      value  # this is also a comment

Comments are not processed during final output

---

### Testing 

pip install pytest

shell> cd tests

shell> pytest -sv run_tests.py


---

## TO DO:

