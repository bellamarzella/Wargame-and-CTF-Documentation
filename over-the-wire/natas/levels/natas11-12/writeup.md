# Natas Level 11 → 12
## Technical Overview
* **Vulnerability Class:**: Insecure Session Management & Weak Cryptography
* **Impact:**: Privilege Escalation, Session Tampering (leading to Information Disclosure)
* **Tools Used:**: Burp Suite, CyberChef

## Sumnmary
The application stores access control flags client-side, in a cookie named `data`, relying on a simple, reversible XOR operation with a static key to protect it's integrity. Because the XOR operation is symmetric and the key is static, we can easily calculate the secret key to forge a cookie with elevated privileges. 

## Vulerable Code Snippet
```php
// The default configuration parameters stored in the cookie
$defaultdata = array( "showpassword"=>"no", "bgcolor"=>"#ffffff");

function xor_encrypt($in) {
    $key = '<hidden_secret_key>';
    $text = $in;
    $outText = '';

    // Iterate through each byte and XOR it with the repeating key
    for($i=0;$i<strlen($text);$i++) {
        $outText .= $text[$i] ^ $key[$i % strlen($key)];
    }

    return $outText;
}

// Decoding, decrypting, and parsing the client's cookie without server-side validation
$tempdata = json_decode(xor_encrypt(base64_decode($_COOKIE["data"])), true);
```

## Exploitation Walkthrough

### Step 1: Recovering the Secret Key
XOR ($\oplus$) has a convenient mathematical property, it is symmetrical. This means that, if we know the plaintext and resulting ciphertext, we can derive the secret key.
$$
Plaintext \oplus Key = Ciphertext \implies Key = Plaintext \oplus Ciphertext
$$

By choosing an arbitrary background colour and grabbing its associated cookie (`EGAgHwQ1...`), we can do the following:
1. Construct the JSON representation of the input data: `{"showpassword":"no","bgcolor":"#ffffff"}`
2. Find the ciphertext by base64-decoding the cookie value.
3. XOR the plaintext and ciphertext to derive the secret key.

### Step 2: Forging the Payload
Now we have the key, we can encrypt any JSON payload. By simply switching the `showpassword` value to `yes` and encrypting it with the derived key, we get a new ciphertext.
$$
New_Plaintext \oplus Key = New_Ciphertext
$$
Base-64 encoding this results in our new malicious cookie value.

### Step 3: Executing the Attack
1. We configure Burp Suite to intercept outgoing browser traffic.
2. We replace the original `data` cookie with our newly forged value.
3. Upon forwarding the request, the server decrypts our cookie, sees `showpassword` set to `yes`, and reveals the password for the next level.

## Remediation
**Store Session State Server-Side:** Never store privilege levels, access control flags or authentication states client-side. Instead, keep this information inside a secure, server-side session database and assign a randomly generated, cryptographically secure session identifier to the client. This prevents tampering and ensures that sensitive information is never exposed to the client.
**Used Signed or Encrypted Cookies:** If you must store information client-side, use signed or encrypted cookies with a strong cryptographic algorithm (e.g., AES) and a unique key per session. This ensures that even if the cookie is intercepted, it cannot be tampered with or decrypted without the key. 