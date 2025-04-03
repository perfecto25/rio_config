# FLEX

Flexible Markup Language is a markup language for use in common configuration scenarios.

It is similar to TOML in concept, but is unique in its approach to handling variables and configuration data

## features

- no spacing requirements (yaml)
- braces not necessary (json)
- clean and simple syntax to describe complex data structures
- ability to create template blocks for repeated options
- ability to pass raw strings without using escape sequences
- can natively ingest shell environment variables at runtime




## flags


@use - use template (must match template name)

@template - create new template


    [@template red]
    template key = this is a red value

    [@template blue]
    template key = this is a blue value

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
            "template key": "this is a red value",
            "roses": "are red"
          },
          "violet": {
            "template key": "this is a blue value",
            "violets": "are blue"
          },
          "tulip": {
            "template key": "this is a red value",
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

to pass a default fallback value if env variable isnt set, provide a default using the double colon

    [database.credential]
    password = @env DB_PASSWORD:abracadabra123


this will use "/opt/default" as the fallback value



### Raw String

@raw - use raw input 

    [check:process:custom]
    match = @raw /home/user/myprocess.*$

