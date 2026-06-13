import re


def get_bug_explanation(bug_type):
    explanations = {
        "Potential debug code found": "The presence of console.log indicates debug code that should be removed before production deployment.",
        "Potential XSS vulnerability found": "Use of eval, document.write, or innerHTML can allow attackers to inject and execute malicious scripts.",
        "Potential infinite loop found": "A loop condition that is always true (e.g. while(true)) will hang the browser unless there is a guaranteed break.",
        "Insecure direct object reference": "Accessing window properties via string keys without validation can expose internal objects to manipulation.",
        "Insecure CORS configuration": "Setting withCredentials=true on cross-origin requests without strict origin checks exposes session data.",
        "Unvalidated input from URL parameters": "Reading from location.search or hash without sanitization allows URL-based injection attacks.",
        "Potential XSS or CSRF vulnerability (insecure use of cookies)": "Setting cookies via document.cookie without HttpOnly/Secure flags makes them accessible to scripts and plain HTTP.",
        "Potential XSS or data leakage (insecure use of local storage)": "Storing sensitive data in localStorage exposes it to any script running on the page.",
        "Use of deprecated or vulnerable library": "Bundling libraries by filename pattern may indicate outdated versions with known CVEs.",
        "Potential privacy or security issue (insecure use of JavaScript APIs)": "Reading navigator, screen, location, or history without user consent may violate privacy regulations.",
        "Insecure randomness (Math.random() usage)": "Math.random() is not cryptographically secure and must not be used for tokens, passwords, or session IDs.",
        "Potential data leakage (insecure client-side encryption)": "Client-side encryption exposes keys in the source; sensitive data should be encrypted server-side.",
        "Potential security issue (WebSocket usage — verify origin validation)": "WebSocket connections should validate the origin header to prevent cross-site WebSocket hijacking.",
        "Potential privacy issue (insecure use of geolocation API)": "Accessing geolocation without clear user consent and HTTPS violates browser security policies.",
        "Potential information disclosure (insecure use of FileReader API)": "Reading user files without strict type validation can expose unexpected data to the application.",
        "Potential XSS or security issue (insecure use of postMessage API)": "postMessage listeners must verify the sender's origin to prevent cross-origin message injection.",
        "Inline JavaScript found": "Inline scripts prevent Content Security Policy enforcement and mix behaviour with markup.",
        "Missing alt attribute in img tag found": "img tags without alt attributes break accessibility and hurt SEO.",
        "Empty or placeholder link found": "Links with href=\"#\" or empty href do not navigate anywhere and should be replaced with real targets.",
        "Missing doctype declaration found": "Omitting <!DOCTYPE html> triggers browser quirks mode, causing inconsistent rendering.",
        "Insecure content loading found (HTTP content on HTTPS page)": "Loading HTTP sub-resources on an HTTPS page triggers mixed-content warnings and blocks in modern browsers.",
        "CSRF vulnerability (missing CSRF token)": "Forms without a CSRF token allow attackers to forge requests on behalf of authenticated users.",
        "Open redirect vulnerability": "An unvalidated redirect_uri parameter lets attackers redirect users to malicious sites after authentication.",
    }
    for key in explanations:
        if key.startswith("Deprecated HTML attribute"):
            explanations[key] = "This attribute is deprecated in HTML5 and may not be supported in modern browsers."
    return explanations.get(bug_type, "No explanation available.")


def scan_js_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    bugs = []

    if re.search(r'\bconsole\.log\b', content):
        bugs.append(("Potential debug code found", file_path))

    if re.search(r'\b(?:eval|document\.write|innerHTML)\b', content):
        bugs.append(("Potential XSS vulnerability found", file_path))

    if re.search(r'for\s*\(\s*;\s*;\s*\)|while\s*\(\s*(true|1|!0)\s*\)', content):
        bugs.append(("Potential infinite loop found", file_path))

    if re.search(r'window\[\s*["\'].*?["\']\s*\]', content):
        bugs.append(("Insecure direct object reference", file_path))

    if re.search(r'XMLHttpRequest\.withCredentials\s*=\s*true', content):
        bugs.append(("Insecure CORS configuration", file_path))

    if re.search(r'location\.search|\.hash\b', content):
        bugs.append(("Unvalidated input from URL parameters", file_path))

    if re.search(r'document\.cookie\s*=', content):
        bugs.append(("Potential XSS or CSRF vulnerability (insecure use of cookies)", file_path))

    if re.search(r'localStorage\s*[\[.]', content):
        bugs.append(("Potential XSS or data leakage (insecure use of local storage)", file_path))

    if re.search(r'angular\.js|jquery\.js|prototype\.js|react\.js|vue\.js', content):
        bugs.append(("Use of deprecated or vulnerable library", file_path))

    if re.search(r'navigator\.|screen\.|window\.location\b|document\.referrer\b|history\.', content):
        bugs.append(("Potential privacy or security issue (insecure use of JavaScript APIs)", file_path))

    if re.search(r'Math\.random\b', content):
        bugs.append(("Insecure randomness (Math.random() usage)", file_path))

    if re.search(r'CryptoJS\.AES|SJCL', content):
        bugs.append(("Potential data leakage (insecure client-side encryption)", file_path))

    if re.search(r'WebSocket\s*\(', content):
        bugs.append(("Potential security issue (WebSocket usage — verify origin validation)", file_path))

    if re.search(r'navigator\.geolocation\s*\.', content):
        bugs.append(("Potential privacy issue (insecure use of geolocation API)", file_path))

    if re.search(r'FileReader\s*\(', content):
        bugs.append(("Potential information disclosure (insecure use of FileReader API)", file_path))

    if re.search(r'window\.postMessage\s*\(', content):
        bugs.append(("Potential XSS or security issue (insecure use of postMessage API)", file_path))

    return bugs


def scan_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    bugs = []

    if re.search(r'<script[^>]*>[^<]*<\/script>', content):
        bugs.append(("Inline JavaScript found", file_path))

    if re.search(r'<img\s+[^>]*>', content) and not re.search(r'alt\s*=\s*".*?"', content):
        bugs.append(("Missing alt attribute in img tag found", file_path))

    if re.search(r'href\s*=\s*"(?:#|javascript:void\(0\)|)"\s*', content):
        bugs.append(("Empty or placeholder link found", file_path))

    if not re.search(r'<!DOCTYPE html>', content, re.IGNORECASE):
        bugs.append(("Missing doctype declaration found", file_path))

    if re.search(r'<(iframe|script|img|link|embed|object)\s+[^>]*\bsrc\s*=\s*"[^"]*http://', content, re.IGNORECASE):
        bugs.append(("Insecure content loading found (HTTP content on HTTPS page)", file_path))

    if re.search(r'<form[^>]*>', content) and not re.search(r'\bcsrf\b', content, re.IGNORECASE):
        bugs.append(("CSRF vulnerability (missing CSRF token)", file_path))

    if re.search(r'\bredirect_uri\s*=\s*"[^"]+', content):
        bugs.append(("Open redirect vulnerability", file_path))

    deprecated_attributes = ['align', 'bgcolor', 'border', 'cellpadding', 'cellspacing']
    for attribute in deprecated_attributes:
        if re.search(fr'\b{attribute}\s*=', content):
            bugs.append((f'Deprecated HTML attribute "{attribute}" found', file_path))

    return bugs
