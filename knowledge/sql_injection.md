# SQL injection

## What it is
SQL injection happens when untrusted input is pasted into a SQL string (f-strings, + concatenation, % formatting or .format()). The input can then change the meaning of the query, for example by returning every row in a table.

## Recommended fix
Use parameterized queries. Keep the SQL text constant and pass the values separately, for example cursor.execute("SELECT id FROM users WHERE username = ?", (name,)) with sqlite3. The placeholder is ? for sqlite3 and %s for most other database drivers. Never build the SQL string from user input.

## Common mistakes
Escaping quotes by hand or blocking words such as OR is not a real fix. Do not rename functions, change signatures or change return shapes while fixing, or the existing tests will break. Table and column names cannot be parameterized; if they must vary, check them against a fixed allow-list.

## How to verify
An exploit test should send a payload such as ' OR '1'='1 and assert that no extra rows come back. The normal-behavior tests must keep passing after the fix.