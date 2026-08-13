# Natas Level 16 → 17 

## Technical Overview
* **Vulnerability Class:** Boolean-based Blind OS Command Injection
* **Impact:** Unauthorised Access to Filesystem leading to Sensitive Information Disclosure.
* **Tools Used:** Python.

## Summary
The webpage contains a single input field that searches a dictionary with `grep` using `passthru()`. There are some input sanitisation measures in place, but they are not sufficient to prevent command injection. Specifically, we can use command substitution to perform a blind OS command injection, allowing us to determine the password one character at a time.

## Vulnerable Code Snippet
```php
passthru("grep -i \"$key\" dictionary.txt");
```

## Exploitation Walkthrough
### Step 1: Understanding the Vulnerability
At first, this seems identical to level 10, but there is a key difference. The `$key` variable is surrounded by double quotes, which means that we cannot use URL encoded newlines to inject additional commands. However, `$()` command substitution is still possible, allowing us to inject our own commands and use the result as a search term in the dictionary. For example, the following input will search for the string `test` in the dictionary:
```bash
$(echo test)
```
### Step 2: Exploiting the Vulnerability
When `grep` fails to find a match, it returns the empty string. If not, it returns something. `grep`-ing the empty string is equivalent to searching for every line in the dictionary, which means the entire dictionary will be returned. If the `grep` finds a match, it will return a subset of the dictionary. 
Using command substitution, we can `grep` the password file one character at a time, and the resulting output will tell use whether the character we guessed is correct or not. For example, the following input will check if the first character of the password is `a`:
```bash
$(grep -o ^a /etc/natas_webpass/natas17)
```

### Step 3: Crafting a Brute Force Script
Now, we simply need to create a script that brute forces the password for us. We can use the fact that, when the response is too large, the server will use Chunked Transfer Encoding. For our purposes, this means that the `Content-Length` header will be missing from the response if the full dictionary is returned, telling us whether our guess was correct or not:
```python
if response.headers.get('Content-Length') != None: # If the grep returns nothing, ie our guess was wrong, then the webpage returns the entire dictionary. If it doesn't do this, we know our guess was right.
                                                    # Content-Length is None because if a response is too large, it is streamed in chunks, and therefore the Content-Length must be found at arrival. In this case this works in our favour.
    password += guess
```
Unlike the previous level which uses SQL, we cannot get away without some improvements in efficiency. The `passthru()` has to spin up a new Bash environment for every request, which is significantly slower. So, this time we use threading, creating a new thread for each character in the character set and checking them all at once:
```python
for guess in charset: # Create a thread for every character in the charset. Each thread tries a single character.
t = threading.Thread(target=check_element, args = (guess,))
threads.append(t)
```
Otherwise, the script is very similar to the previous level, and can be found [here](./16.py).

## Remediations
*Standard command injection and brute-force mitigations apply, but I feel they aren't worth repeating ad nauseam. For completeness, relevant strategies are listed without further explanation below:*
- **Input Validation and Sanitisation**
- **Disable Command Execution via Web Server Configuration**
- **Rate Limiting**
