# FML


Flexible Markup Language is a markup language for use in common configuration scenarios.

It is similar to TOML in concept, but is unique in its approach to handling variables and configuration data

## features

- no spacing requirements (yaml)
- braces not necessary (json)
- clean and simple syntax to describe complex data structures
- ability to create template blocks for repeated options
- ability to pass raw strings without using escape sequences
- PAML can natively ingest shell environment variables at runtime



deep hash

```
[check:filesystem:home]
name = "/home"

[check:filesystem:opt]
name = "/opt"