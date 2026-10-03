# Path traversal

## What it is
Path traversal happens when a user-controlled file name is joined to a directory without checking where the result points, so input such as ../../secret.txt can read files outside the intended folder.

## Recommended fix
Resolve the final path and check that it stays inside the base directory, for example with pathlib: base = Path(BASE).resolve(); target = (base / name).resolve(); then reject the request unless target is inside base (target.is_relative_to(base)). Prefer an allow-list of known file names when possible.

## Common mistakes
Removing the string ../ once is not enough, because encoded or nested forms can survive. Do not check the path before resolving it.

## How to verify
An exploit test requests ../ style names and asserts that access is refused. Normal file requests must still work.