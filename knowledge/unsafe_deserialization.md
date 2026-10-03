# Unsafe deserialization

## What it is
Loading untrusted data with pickle, or with yaml.load without a safe loader, can run attacker-controlled code while the data is being read.

## Recommended fix
Use a data-only format such as JSON for untrusted input. For YAML use yaml.safe_load. Never unpickle data that came from a user or from the network.

## Common mistakes
Checking the data after loading it is too late, because the code has already run. Wrapping pickle.loads in try and except does not make it safe.

## How to verify
An exploit test passes a harmless payload that would set a flag if code ran, and asserts that the flag stays unset and the input is rejected. Normal valid input must still load.