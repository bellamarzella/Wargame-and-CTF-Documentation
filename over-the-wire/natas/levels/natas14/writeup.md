# Natas Level 14 → 15

## Technical Overview
* **Vulnerability Class:** SQL Injection
* **Impact:** Unauthorised Access to Database leading to Sensitive Information Disclosure.
* **Tools Used:** Browser.

## Summary
The webpage contains a login form that is left completely unprotected against SQL Injections. The application takes raw user input and directly inserts it into an SQL query without any sanitisation or validation. This allows us to inject our own SQL code into the query, bypassing authentication and retrieving sensitive information from the database.

## Vulnerable Code Snippet
```php
$query = "SELECT * from users where username=\"".$_REQUEST["username"]."\" and password=\"".$_REQUEST["password"]."\"";
```

## Exploitation Walkthrough
The PHP snippet above constructs the following SQL query:
```sql
SELECT * from users where username="[INPUT]" and password="[INPUT]"
```
If, for one of our inputs (easier to parse if we use the password field), we include a `"` character, we break out of the string context and can append our own SQL code. For example, inputting the following into the password field reveals the entire users table:
```sql
test" or "1=1
```
This makes the query:
```sql
SELECT * from users where username="test" and password="test" or "1=1"
```
Which yields the password.

## Remediations
- **Reducing Information Disclosure:** When we query a database, we should never return more information than is necessary. Level 14 just returns the result of the query, which is how we are able to retrieve the password. Level 15 implements this remediation by only returning whether a user exists or not.
- **Input Validation and Sanitisation:** We should always validate and sanitise user input, ensuring that it is of the expected type and format. This can be done with regular expressions, or by using built-in functions like `filter_var()` in PHP. However, this should not be relied upon as the sole defence against SQL injection, as it can be bypassed. 
- **Prepared Statements:** Prepared statements are a way to parameterise SQL queries, allowing us to separate the query from the data. This means that the data is never directly inserted into the query, preventing SQL injection attacks. In PHP, we can use the `mysqli` or `PDO` libraries to create prepared statements.