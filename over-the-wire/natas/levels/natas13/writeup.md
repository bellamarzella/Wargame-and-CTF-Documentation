# Natas Level 13 → 14

## Technical Overview
* **Vulnerability Class:** Unrestricted File Upload.
* **Impact:** Remote Code Execution leading to Local File Read.
* **Tools Used:** Burp Suite.

## Summary
As with Level 12, the application allows users to upload files and modify the `filename` parameter of the POST request to change the extension. The difference here is that the file type is now enforced on the server-side with `exif_imagetype()`. However, this function checks file type by verifying the magic bytes of the file. We can simply insert the magic bytes of a JPEG file `FF D8 FF E1` before our PHP payload and the server will accept it as a valid JPEG file. Once uploaded, we can access the file directly and execute arbitrary code on the server, leading to a Local File Read vulnerability.

## Exploitation Walkthrough
### Step 1: Creating the Payload
To create our [malicious payload](./13.php), we use the same PHP code as in Level 12, modified to read the contents of `/etc/natas_webpass/natas14` instead. In the script, you'll find `AAAA` as a placeholder for our magic bytes; this just makes it easier to identify where to insert them.
```php
AAAA<!DOCTYP...
```
### Step 2: Uploading and Executing the Payload
This is simpler using Burp Suite to intercept the request and modify it before it reaches the server. As with 12, we change the file extension from `.jpg` to `.php`, but we also insert the magic bytes `FF D8 FF E1` before our PHP payload in the Hex tab; replacing the `AAAA` placeholder. Once uploaded, we are taken to a confirmation page with a link to the uploaded file. Clicking the link executes our payload and displays the password.


## Remediations
- **Move uploads outside of the webroot:** This would prevent direct access to uploaded files, making it harder for an attacker to execute arbitrary code on the server.
- **Disable Script Execution via Web Server Configuration:** This can be done by adding a `.htaccess` file to the upload directory with the following content:
``` 
<FilesMatch "\.(php|php5|phtml|html|htm)$">
    Order Allow,Deny
    Deny from all
</FilesMatch>
```
