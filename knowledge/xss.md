# Cross-site scripting (XSS)

## What it is
Cross-site scripting happens when user input is placed into an HTML page without escaping, so an attacker's text such as a script tag runs as real code in other visitors' browsers.

## Recommended fix
Escape user-controlled values before they go into HTML. In Flask use markupsafe.escape(value) or html.escape(value), or render with a Jinja template, which escapes variables automatically. Keep the surrounding markup unchanged and escape only the user value.

## Common mistakes
Removing the word script is not a fix, because other tags and attributes can also run code. Do not mark user input as safe with Markup or the safe filter. Do not change the function name or the HTML structure while fixing.

## How to verify
An exploit test passes a name such as a script tag and asserts that the raw tag is not in the output, since an escaped version is fine. Normal names must still render the same page.