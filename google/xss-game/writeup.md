# Google's XSS Game

| Level | Objective | Solution | 
| :--- | :--- | :--- | 
| **1** | Reflected XSS caused by echoing un-sanitised search query input directly into the page's raw HTML context. | Pasted a payload (`<script>alert()</script>`) into the search field. | 
| **2** | Stored XSS where user comments are saved to a database and rendered without stripping HTML event handlers like `onerror`. | Comments are loaded dynamically so previous payload doesn't work. Commented the following payload instead: `<img src=x onerror=alert(1)>`. |
| **3** | DOM-based XSS where a client unsafely concatenates a URL hash fragment directly into an `<img>` tag's `src` attribute. | Appended `x5.jpg' onerror='alert()` onto the URL. |
| **4** |  Reflected XSS inside an inline script context where unescaped input allows breaking out of a JavaScript string literal argument. | Searched for `'); alert('`, breaking out of a `startTimer` function and calling `alert()` on page load. |
| **5** | DOM-based XSS where an unvalidated query parameter is injected directly into an anchor tag's `href` attribute, allowing protocol manipulation. | Replaced the `confirm` in `next=confirm` with  `javascript:alert()` in the URL, modifying the button to show an alert rather than take us to a different page. |
| **6** | DOM-based XSS where a gadget file dynamically fetches and evaluates an external script specified via a filtered URL parameter, bypassed using a data URI. | Appended `data:text/javascript,alert()` to the frame parameter. |