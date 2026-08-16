# Google's XSS Game

| Level | Objective | Solution | 
| :--- | :--- | :--- | 
| **1** | Reflected XSS via direct server-rendered HTML response. | Pasted a payload (`<script>alert()</script>`) into the search field. | 
| **2** | Stored XSS rendered dynamically via `innerHTML`. | Comments are loaded dynamically so previous payload doesn't work. Commented the following payload instead: `<img src=x onerror=alert(1)>`. |
| **3** | DOM-based XSS via URL hash fragment rendered dynamically via client-side string concatenation into `innerHTML` | Appended `x5.jpg' onerror='alert()` onto the URL. |
