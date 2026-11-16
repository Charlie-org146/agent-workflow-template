# Lower the template's min_free_memory_gb from 3.5 to 3.0 until v1.0.0 is released (owner record o39, Guardrails)

- Slug: memory-floor-3
- Touches: .loop/config.json

## Done lines

Frozen. A wrong done line needs a new goal.

1. .loop/config.json has "min_free_memory_gb": 3.0 as a one-line change with no other change, the shipped default stays 4, and the commit cites o39

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
