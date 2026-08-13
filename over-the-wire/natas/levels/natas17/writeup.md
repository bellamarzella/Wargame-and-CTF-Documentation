# Natas Level 17 → 18 

## Technical Overview
* **Vulnerability Class:** Time-based Blind SQL Injection.
* **Impact:** Unauthorised Access to Database leading to Sensitive Information Disclosure.
* **Tools Used:** Python.

## Summary
This level is very similar to [level 15](../natas15/writeup.md), but the application no longer returns any information when we query the database, ruling out our previous boolean-based attack. However, the application is still wide open to SQL Injection, and so we can use a time-based blind SQL injection to brute force the password one character at a time.  

## Exploitation Walkthrough
### Step 0: How does this differ from level 15?
Looking at the the source code, we can see one key difference between this level and level 15. The `echo` lines have been commented out:
```php
if(mysqli_num_rows($res) > 0) {
        // echo "This user exists.<br>";
```
This means we cannot use the response to determine whether our guess was correct or not, ruling out our previous boolean-based attack. However, the code is otherwise unchanged and thus still vulnerable to SQL Injections.

### Step 1: Understanding time-based blind SQL injections
Seeing as we can't rely on the server to tell us whether our guess was correct or not, we need to inject our own response. This is where time-based blind SQL injections come in. The idea is to use the `sleep()` function to determine whether a guess was correct or not:
```sql
SELECT * FROM users WHERE username='natas18' AND IF(1=1, sleep(5), 0) 
```
In this case, if our condition `1=1` is true, then we wait for 5 seconds. If not, then we respond immediately.
### Step 2: Building the script
Now we just need to turn this into an injection. We can borrow the structure of the injection from level 15, adding our `IF` and `SLEEP` functions:
```python
payload = {"username": f'natas18" AND IF((BINARY SUBSTRING(password, {i}, 1) = "{guess}"), SLEEP(1), 0) -- "' # If our guess is correct, wait an implausible amount of time, if not, do nothing     }
```
We can also modify the script to add a character based on the amount of time passed rather than the content of the response:
```python
if response.elapsed.total_seconds() > 1: # then we guessed correctly
```
Finally, just put it all together in a loop and we can brute force the password one character at a time.

## Remediations
*Standard SQLi and brute-force mitigations apply, but I feel they aren't worth repeating ad nauseam. For completeness, relevant strategies are listed without further explanation below:*
- **Input Validation and Sanitisation**
- **Parameterised Queries**
- **Rate Limiting**
