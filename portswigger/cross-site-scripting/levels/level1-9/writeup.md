# Level 1 → 9

| Level | Description | Solution | Note |
| :--- | :--- | :--- | :--- |
| **1** | Reflected XSS into HTML context with nothing encoded. | Typed the payload into the search field. |  |
| **2** | Stored XSS into HTML context with nothing encoded. | Added the payload as a comment on the blog. |  |
| **3** | DOM-based XSS in `document.write()` sink using source `location.search`. | Escaped out of `<img>` tag to trigger an alert. |  |
| **4** | DOM XSS in `innerHTML` sink using source `location.search`. | Searched for `<img src=x onerror=alert()>` |  |
| **5** | DOM XSS in jQuery anchor `href` attribute sink using `location.search` source. | The back button gets it's `href` attribute from the `returnpath=` URL parameter. We can replace the default parameter `/` with `javascript:alert(document.cookie)` to force the back button to execute the alert. | While it isn't an actual exploit, there is an interesting feature which could be exploited. The JavaScript has a branch for if the `personal` attribute exists on the form. By adding it ourselves we enable that branch which opens up the possibility of a reflected XSS attack. The `name` input is used as `innerHTML` in this branch, so we can use a payload such as `<img src=x onerror=alert()>` to trigger an alert. |
| **6** | DOM XSS in jQuery selector sink using a `hashchange` event. | We identified that the application uses an old version of jQuery (1.4.1), which treats any string containing HTML as code and immediately executes it. The application listens for a `hashchange` event to automatically scroll the page to a specific blog entry. Because the event reads directly from the URL hash, we can inject a malicious payload into the URL. By embedding this poisoned URL inside an iframe and delivering it to a victim, the script executes automatically, successfully completing the lab. |  |
| **7** | Reflected XSS into attribute with angle brackets HTML-encoded. | Search for a random string, observe it appears within the search box and thus must appear as the value of teh `value` attribute. We can break out with a `"` and then add a new attribute, such as `onmouseover` which triggers a payload. | |
| **8** | Stored XSS into anchor `href` attribute with double quotes HTML-encoded. | Fill out comment details, observe that, if a website is provided, the username is used as the anchor text and the website is used as the `href` attribute. We can use `javascript:[payload]` as the website to trigger a payload when the username is clicked. |  |
| **9** | Reflected XSS into a JavaScript string with angle brackets HTML encoded. | Using Burp Suite's Repeater, we can observe that the search box input modifies the JavaScript code. By searching for `'; alert(); //` We can escape the `searchTerms` variable assignment, add our `alert()` payload and comment out anything after. |  |
                         

 