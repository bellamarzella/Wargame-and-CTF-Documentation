# Natas Level 12 → 13

## Technical Overview
* **Vulnerability Class:** Unrestricted File Upload.
* **Impact:** Remote Code Execution leading to Local File Read.
* **Tools Used:** Browser Dev Tools.

## Summary
The application allows users to upload files without proper validation or sanitisation. The only restriction is that the name of the file is randomised and the file extension is forced to be `.jpg`. However, the extension is enforced on the client-side only, meaning we can change the extension to `.php` and upload a malicious PHP script. Once uploaded, we can access the file directly and execute arbitrary code on the server, leading to a Local File Read vulnerability.

## Vulnerable Code Snippet

```php
<input type="hidden" name="filename" value="<?php print genRandomString(); ?>.jpg" /> // Client side enforces the extension to be .jpg, however we can just change this to whatever we want.

$ext = pathinfo($fn, PATHINFO_EXTENSION); // Server blindly trusts the extension provided by the client.
```

## Exploitation Walkthrough
### Step 1: Creating the Payload 
To create our [malicious payload](./script.php), we can use the following PHP code to read the contents of `/etc/natas_webpass/natas13`:

```php
$password = fopen("/etc/natas_webpass/natas13", "r") or die("error");
echo fread($password, filesize("/etc/natas_webpass/natas13"));
```

### Step 2: Uploading and Executing the Payload
We then simply select the payload, edit the file extension from `.jpg` to `.php` using devtools and then upload the file. Once uploaded, we are taken to a confirmation page with a link to the uploaded file. Clicking the link executes our payload and displays the password.

## Remediation
- **Hardcode the Extension:** The server should enforce the file extension, not the client. This can be done by checking the file extension on the server-side and rejecting any files that do not match the expected extension.
- **Validate File Type:** The server should validate the file type by checking the MIME type of the uploaded file. This can be done using PHP's `finfo_file()` function.