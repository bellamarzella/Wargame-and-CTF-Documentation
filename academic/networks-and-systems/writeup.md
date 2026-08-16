# Networks and Systems - Cybersecurity Submodule Coursework Writeup

## 1. Caesar Cipher Cryptanalysis
**Difficulty:** Low

### Walkthrough
The payload was encoded using a Caesar cipher. Knowing common structural patterns in challenge outputs, I aligned the expected prefix against the ciphertext string. This revealed the key offset as `+1`. Applying this key offset to the rest of the encoded string produced the plaintext solution.

### Vulnerability Analysis
The Caesar cipher is a simple substitution cipher and is highly vulnerable to brute-force attacks or pattern recognition. In this case, the use of a known phrase made reverse engineering the key trivial. This vulnerability is low severity, as it does not compromise sensitive data or system integrity but fails to provide meaningful protection.

### Remediation
* Use a modern encryption standard such as AES-256.
* If a simple cipher must be used for lightweight encoding, avoid predictable phrases in the text to make reverse engineering more difficult.
* Implement rate-limiting mechanisms to prevent automated testing.


## 2. Attribute-Based Access Control (ABAC) Policy Bypass
**Difficulty:** Low

### Walkthrough
Listing hidden files revealed the policy as a hidden text file. Analyzing it showed that `OSA` is permitted if `GGID=True`, `OSB` is denied if `CUOU=True`, and `OSC` is denied if `VWVP=True`. Knowing these conditions had to hold true regardless of other attributes, I began testing URLs. `GGID=True` was denied, and so was `GGID=True&CUOU=False`, but `GGID=True&CUOU=False&VWVP=False` happened to return the target output without having to consider the rest of the policy.

### Vulnerability Analysis
Access decisions rely solely on a small subset of attributes, simplifying the attack surface and allowing attackers to bypass the intended complexity of the policy. This presents a low severity vulnerability, as it compromises the access control mechanism but does not expose sensitive data directly or allow full system compromise.

### Remediation
* Enforce rate-limiting or CAPTCHA mechanisms in the ABAC system to prevent systematic testing of attributes.
* Redesign policies to require full evaluation of all conditions before granting access.


## 3. Unencrypted UDP Data Transmission & Traffic Sniffing
**Difficulty:** Low–Medium

### Walkthrough
Inspecting the web root revealed an HTML comment containing the endpoint `/pingme…`. To discover how the data was transmitted, I captured all web traffic using `tcpdump -i any -n` while triggering the endpoint. This revealed UDP packets being sent to port `1223`. I set up a netcat listener on that port using `nc -u -l -p 1223`, triggered the endpoint in another terminal, and received a base64 encoded payload, which revealed the secret when decoded.

### Vulnerability Analysis
Sensitive data is transmitted unencrypted over UDP without any authentication mechanism. Anyone with network access can listen for and capture the packet. The data is sent in cleartext and there are no access controls preventing unauthorised users from receiving it.

### Remediation
* Encrypt UDP traffic using DTLS or transition to a secure protocol such as HTTPS.
* Implement authentication mechanisms to verify the recipient before transmitting sensitive data.
* Store sensitive information securely rather than hardcoding it into endpoints.


## 4. Insecure Key Storage & RSA-SHA256 Digital Signatures
**Difficulty:** Low–Medium

### Walkthrough
This challenge requires generating an RSA-SHA256 signature for a provided string and verifying it through the webpage. I used `echo -n` to save the exact message to a text file, then signed it using `openssl dgst…` with the provided private key and passphrase. I base64 encoded the result and submitted it, giving me the obfuscated output which I decoded using `atob()`.

### Vulnerability Analysis
This challenge simulates signature-based access but prioritises usability over strict security. The private key was freely accessible, meaning anyone could generate a valid signature and retrieve the secret. In a real-world system, this would pose a serious risk.

### Remediation
* Utilize hardware-backed key storage solutions (e.g., HSMs or TPMs).
* Enforce periodic key rotation policies.
* Implement multi-factor authentication (MFA) for administrative signature operations.


## 5. DOM-based XSS & Client-Side Authentication Bypass
**Difficulty:** Medium

### Walkthrough
The webpage hashes a user-provided password and compares it to a hardcoded hash. While doing this client-side is inherently unsafe, I discovered this could be completely bypassed by modifying the DOM directly in the browser. I added a new input field and button that echoed the input back into the page with no sanitisation. This allowed me to inject a reflected XSS payload:
```html
<img src=x onerror="location.href='[...]/secure.php'">
```

This redirected me to the secret payload, obfuscated with base64, which I decoded using `atob()`.

### Vulnerability Analysis
The absence of a Content Security Policy (CSP) is a severe flaw that allowed DOM modification and XSS execution to bypass the password logic. Performing password verification client-side is an additional architectural flaw.

### Remediation
* Perform all authentication and password checks server-side.
* Properly sanitise and output-encode all user input to prevent script injection.
* Enforce a strict Content Security Policy (CSP) to restrict inline script execution.


## 6. HTTP PCAP Packet Analysis & OpenSSL Decryption
**Difficulty:** Medium

### Walkthrough
I opened the `.pcap` file in Wireshark and filtered HTTP traffic to trace the key exchange protocol. A request with `getSecret=NJZS5fL88n` revealed the encryption key, and the corresponding response began with `U2FsdGVkX1`, identifying it as an OpenSSL-encrypted payload using a passphrase-derived key and salt. I decrypted it using the following command to reveal the payload:
```bash
openssl enc -aes-256-cbc -d -a -pbkdf2 -pass pass:[secret]
```

### Vulnerability Analysis
Transmitting sensitive cryptographic material (keys and encrypted data) over unencrypted HTTP allows attackers to intercept it via network sniffing. This represents a medium-severity vulnerability as the underlying system is not compromised directly.

### Remediation
* Enforce TLS/HTTPS encryption across all communication channels.
* Implement Ephemeral Elliptic Curve Diffie-Hellman (ECDHE) key exchange instead of static key transmission.
* Utilize short-lived session tokens with strict expiration policies.
* Add HMAC signatures to verify data integrity and prevent tampering.


## 7. Broken Password Hashing & Predictable OTP
**Difficulty:** Medium-High

### Walkthrough
I audited `getflag.c` and identified a target city MD5 hash (`4cfe2ff7b13790305d177d7c4bc5a9b4`), a hardcoded salt (`Bu4N9`), and a time-dependent OTP formula. To crack the hash, I wrote `cityCracker.py` to test salted entries from `worldcities.csv`:

```python
import csv
import hashlib

filename = r"[PATH_TO_WORLD_CITIES_CSV]"
target = "4cfe2ff7b13790305d177d7c4bc5a9b4"
salt = "Bu4N9"

with open(filename, 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    for city in csvreader:
        name = city[0].strip().lower()
        candidate = name + salt
        hashed = hashlib.md5(candidate.encode()).hexdigest()
        if hashed == target:
            print("Target found!")
            print("City:", city[0])
            break
```

Running the script revealed the city `westminster`. I then calculated the required 3-digit OTP using the server's time formula, `abs((((time / 100) * 1234) % 10000) * 1234) % 1000`, based on the current Unix epoch time. Submitting `westminster` and the calculated OTP passed validation and decrypted the flag (`a85e167b3b8d`).

### Vulnerability Analysis
MD5 lacks computational cost and memory hardness, allowing fast offline dictionary attacks when combined with a static salt. Additionally, deriving the OTP from `time(NULL) / 100` creates a deterministic 100-second window, enabling an attacker to compute valid tokens without authentication.

### Remediation
* Replace MD5 with a modern, memory-hard hashing algorithm such as Argon2id using unique per-user salts.
* Replace predictable time-based arithmetic with standard RFC 6238 TOTP (HMAC-SHA256) or a system CSPRNG (`/dev/urandom`).

## 8. Reflected XSS & SQLite Injection
**Difficulty:** Medium–High

### Walkthrough
Building on the previous translator challenge, client-side input filtering was bypassed by injecting an XSS payload via element inspection:
```html
<img src="x" onerror="location.href='localhost/[...]/secureEGIn0O9h.php'">
```
This redirected to a second translator backed by SQLite. Injecting `' OR '1'='1` returned all rows, exposing the raw query structure:
```sql
SELECT french FROM table WHERE english='[input]'
```
I extracted database metadata using a UNION injection:
```sql
' UNION SELECT name FROM sqlite_master WHERE type='table'--
```
This identified a hidden table, from which the secret payload was extracted via `SELECT *`.

### Vulnerability Analysis
The application exhibits high-severity vulnerabilities in both frontend input handling (XSS) and backend data access (SQLi) due to missing input validation and dynamic SQL query construction.

### Remediation
* Use parameterised queries (prepared statements) for all database operations.
* Sanitise and encode all user inputs server-side before processing.
* Enforce a Content Security Policy (CSP) and disable inline script execution.
* Apply Role-Based Access Control (RBAC) on the database user account to restrict table read permissions.


## 9. Insecure Key Exchange Protocol Analysis
**Difficulty:** High

### Walkthrough
I executed the protocol script to observe its key exchange sequence:
1. Party A sends a Base64-encoded `"hello"` to Party B.
2. Party B responds with a Base64-encoded key integer.
3. Party A replies with an OpenSSL-encrypted message (prefixed with `U2FsdGVkX1`).

I decoded the Base64 key from Step 2 and passed it as a passphrase to OpenSSL, successfully decrypting Party A's payload and obtaining the secret.

### Vulnerability Analysis
The protocol transmits its raw encryption key over the network with only Base64 encoding for obfuscation. Because key derivation relies solely on an exposed integer without added entropy or authentication, any network observer can decrypt traffic.

### Remediation
* Implement authenticated key exchange protocols such as Elliptic Curve Diffie-Hellman (ECDH).
* Enforce Perfect Forward Secrecy (PFS) to protect past sessions from future key compromises.
* Never transmit raw encryption keys or key material over the network in plaintext.


## 10. Protocol Manipulation & Session Key Interception
**Difficulty:** High

### Walkthrough
I initiated the key exchange protocol and tampered with the payload to request a session between Party A and Adversary E (instead of Party A and Party B). The server responded with a payload encrypted under $K_{AS}$, containing session key $K$ and $\{K\}_{KES}$. 

I passed this response to Party A, which decrypted it and forwarded $\{K\}_{KES}$ along with $\{flag\}_K$ to Party B. By intercepting this transmission:
1. I decrypted $\{K\}_{KES}$ using my known key $K_{ES}$ to extract session key $K$.
2. I decrypted $\{flag\}_K$ using session key $K$ to reveal the hidden secret.

### Vulnerability Analysis
The protocol lacks authentication and explicit identity-binding between session participants. The server fails to verify recipient identity, allowing an inline adversary to manipulate session requests and recover generated session keys.

### Remediation
* Enforce mutual authentication between all communicating parties.
* Include explicit participant identifiers (e.g., origin and destination IDs) inside encrypted protocol messages.
* Ensure session keys are never encrypted with keys accessible to untrusted third parties.