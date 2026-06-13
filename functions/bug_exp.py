import re


def get_bug_explanation(bug_type):
    explanations = {
        # JS / TS
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
        "Hardcoded secret or credential found": "Secrets embedded in source code can be extracted from version control or compiled bundles; use environment variables instead.",
        "Potential XSS vulnerability (dangerouslySetInnerHTML)": "dangerouslySetInnerHTML bypasses React's XSS protection; sanitize content with a library like DOMPurify before use.",
        "Potential code injection (setTimeout/setInterval with string)": "Passing a string to setTimeout or setInterval is equivalent to eval and can execute injected code.",
        "Insecure HTTP request (should use HTTPS)": "Fetching over plain HTTP exposes data to interception; all network requests should use HTTPS.",
        "Potential prototype pollution": "Modifying __proto__ or constructor.prototype can corrupt shared object behaviour across the entire application.",
        "Type assertion to 'any' bypasses type safety": "Casting to 'any' removes TypeScript's type guarantees and can hide runtime errors or unsafe data handling.",
        # HTML
        "Inline JavaScript found": "Inline scripts prevent Content Security Policy enforcement and mix behaviour with markup.",
        "Missing alt attribute in img tag found": "img tags without alt attributes break accessibility and hurt SEO.",
        "Empty or placeholder link found": "Links with href='#' or empty href do not navigate anywhere and should be replaced with real targets.",
        "Missing doctype declaration found": "Omitting <!DOCTYPE html> triggers browser quirks mode, causing inconsistent rendering.",
        "Insecure content loading found (HTTP content on HTTPS page)": "Loading HTTP sub-resources on an HTTPS page triggers mixed-content warnings and blocks in modern browsers.",
        "CSRF vulnerability (missing CSRF token)": "Forms without a CSRF token allow attackers to forge requests on behalf of authenticated users.",
        "Open redirect vulnerability": "An unvalidated redirect_uri parameter lets attackers redirect users to malicious sites after authentication.",
        "Missing Content-Security-Policy meta tag": "Without a CSP header or meta tag, browsers allow unrestricted script sources, increasing XSS risk.",
        "Sensitive data in GET form (method='GET')": "Form data submitted via GET appears in URLs and server logs; use POST for sensitive fields.",
        "Missing rel='noopener noreferrer' on target='_blank' link": "Links opening in a new tab without noopener give the target page access to window.opener, enabling tab-napping.",
        "Autocomplete enabled on password field": "Browsers may cache the password locally; set autocomplete='off' or 'new-password' on password inputs.",
        "iframe missing sandbox attribute": "iframes without a sandbox attribute can run scripts, submit forms, and access the parent origin.",
        # PHP
        "Unvalidated user input from superglobal": "Using $_GET, $_POST, or $_REQUEST directly without validation or sanitization allows injection attacks.",
        "Use of eval() in PHP": "eval() executes arbitrary PHP code; if unsanitized input reaches it, the server is fully compromised.",
        "Potential command injection (shell execution)": "Passing user input to shell_exec, exec, or system allows attackers to run arbitrary OS commands.",
        "Potential SQL injection (unsanitized query)": "Concatenating variables into SQL queries without prepared statements allows database manipulation.",
        "Hardcoded credential or secret in PHP": "Credentials in PHP source files are exposed to anyone with file-system or repository access.",
        "Potential XSS (direct echo of user input)": "Echoing $_GET or $_POST without htmlspecialchars() writes attacker-controlled HTML directly into the page.",
        "Potential file inclusion vulnerability (LFI/RFI)": "Using a variable in include() or require() allows attackers to load arbitrary local or remote files.",
        "Open redirect in PHP header()": "Redirecting to a user-supplied URL lets attackers craft phishing links that appear to be under your domain.",
        # CSS
        "CSS expression injection (IE legacy)": "The CSS expression() function executes JavaScript in older IE and is a known XSS vector.",
        "Insecure HTTP resource in CSS url()": "Fetching assets over HTTP from an HTTPS page causes mixed-content warnings and can be intercepted.",
        "Insecure @import over HTTP": "@import over HTTP exposes stylesheet loading to man-in-the-middle attacks.",
        "Potentially untrusted @import source": "Importing stylesheets from relative or uncontrolled paths can load attacker-modified CSS if the path is compromised.",
        # JSON
        "Hardcoded secret or credential in JSON": "Secrets in JSON config files are easily leaked via version control or misconfigured static file serving.",
        # ENV
        "Exposed secret or credential in .env file": ".env files must never be committed to version control; add .env to .gitignore and use secret managers in production.",
        # XML
        "Potential XXE (XML External Entity) injection": "SYSTEM entity declarations can force the parser to read local files or make internal network requests.",
        "DOCTYPE with internal subset — possible XXE vector": "Internal subsets in DOCTYPE allow entity declarations that can be exploited for XXE attacks.",
        # SQL
        "Potential SQL injection (string concatenation in query)": "Building queries by concatenating strings enables attackers to alter query logic; use parameterised statements.",
        "Overly permissive GRANT (GRANT ALL PRIVILEGES)": "Granting all privileges gives a user unrestricted database access; apply the principle of least privilege.",
        "Hardcoded password in SQL file": "Passwords stored in plain SQL scripts are exposed to anyone with repository or file access.",
    }
    for key in list(explanations.keys()):
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

    if re.search(r'(apiKey|api_key|password|secret|token)\s*[:=]\s*["\'][^"\']{6,}["\']', content, re.IGNORECASE):
        bugs.append(("Hardcoded secret or credential found", file_path))

    if re.search(r'dangerouslySetInnerHTML', content):
        bugs.append(("Potential XSS vulnerability (dangerouslySetInnerHTML)", file_path))

    if re.search(r'set(?:Timeout|Interval)\s*\(\s*["\']', content):
        bugs.append(("Potential code injection (setTimeout/setInterval with string)", file_path))

    if re.search(r'fetch\s*\(\s*["\']http://', content) or re.search(r'open\s*\(\s*["\'][A-Z]+["\'],\s*["\']http://', content):
        bugs.append(("Insecure HTTP request (should use HTTPS)", file_path))

    if re.search(r'__proto__|constructor\.prototype', content):
        bugs.append(("Potential prototype pollution", file_path))

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

    if not re.search(r'<meta[^>]+http-equiv\s*=\s*["\']Content-Security-Policy["\']', content, re.IGNORECASE):
        bugs.append(("Missing Content-Security-Policy meta tag", file_path))

    if re.search(r'<form[^>]+method\s*=\s*["\']get["\']', content, re.IGNORECASE):
        bugs.append(("Sensitive data in GET form (method='GET')", file_path))

    if re.search(r'target\s*=\s*["\']_blank["\']', content, re.IGNORECASE) and \
       not re.search(r'rel\s*=\s*["\'][^"\']*noopener', content, re.IGNORECASE):
        bugs.append(("Missing rel='noopener noreferrer' on target='_blank' link", file_path))

    if re.search(r'<input[^>]+type\s*=\s*["\']password["\'][^>]*autocomplete\s*=\s*["\']on["\']', content, re.IGNORECASE):
        bugs.append(("Autocomplete enabled on password field", file_path))

    if re.search(r'<iframe(?![^>]*\bsandbox\b)[^>]*>', content, re.IGNORECASE):
        bugs.append(("iframe missing sandbox attribute", file_path))

    return bugs


def scan_php_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    bugs = []

    if re.search(r'\$_(GET|POST|REQUEST|COOKIE|SERVER)\s*\[', content):
        bugs.append(("Unvalidated user input from superglobal", file_path))

    if re.search(r'\beval\s*\(', content):
        bugs.append(("Use of eval() in PHP", file_path))

    if re.search(r'\b(shell_exec|exec|system|passthru|popen)\s*\(', content):
        bugs.append(("Potential command injection (shell execution)", file_path))

    if re.search(r'mysql_query\s*\(.*\$', content) or \
       re.search(r'(SELECT|INSERT|UPDATE|DELETE)[^;]*\'\s*\.\s*\$', content, re.IGNORECASE):
        bugs.append(("Potential SQL injection (unsanitized query)", file_path))

    if re.search(r'(password|passwd|secret|api_key|apikey|token)\s*=\s*["\'][^"\']{4,}["\']', content, re.IGNORECASE):
        bugs.append(("Hardcoded credential or secret in PHP", file_path))

    if re.search(r'echo\s+\$_(GET|POST|REQUEST)', content):
        bugs.append(("Potential XSS (direct echo of user input)", file_path))

    if re.search(r'\b(include|require|include_once|require_once)\s*\(\s*\$', content):
        bugs.append(("Potential file inclusion vulnerability (LFI/RFI)", file_path))

    if re.search(r'header\s*\(\s*["\']Location:\s*["\'\s]*\.\s*\$', content):
        bugs.append(("Open redirect in PHP header()", file_path))

    return bugs


def scan_css_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    bugs = []

    if re.search(r'expression\s*\(', content, re.IGNORECASE):
        bugs.append(("CSS expression injection (IE legacy)", file_path))

    if re.search(r'url\s*\(\s*["\']?http://', content, re.IGNORECASE):
        bugs.append(("Insecure HTTP resource in CSS url()", file_path))

    if re.search(r'@import\s+["\']http://', content, re.IGNORECASE):
        bugs.append(("Insecure @import over HTTP", file_path))

    if re.search(r'@import\s+["\'](?!https?://)', content, re.IGNORECASE):
        bugs.append(("Potentially untrusted @import source", file_path))

    return bugs


def scan_ts_file(file_path):
    bugs = scan_js_file(file_path)

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    if re.search(r'\bas\s+any\b', content):
        bugs.append(("Type assertion to 'any' bypasses type safety", file_path))

    return bugs


def scan_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    bugs = []

    if re.search(
        r'"(password|passwd|secret|api_key|apikey|token|private_key|access_key|auth_token)"\s*:\s*"[^"]{4,}"',
        content, re.IGNORECASE
    ):
        bugs.append(("Hardcoded secret or credential in JSON", file_path))

    return bugs


def scan_env_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    bugs = []

    if re.search(r'(PASSWORD|SECRET|API_KEY|TOKEN|PRIVATE_KEY|ACCESS_KEY)\s*=\s*.+', content, re.IGNORECASE):
        bugs.append(("Exposed secret or credential in .env file", file_path))

    return bugs


def scan_xml_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    bugs = []

    if re.search(r'<!ENTITY\s+\w+\s+SYSTEM\s+["\']', content, re.IGNORECASE):
        bugs.append(("Potential XXE (XML External Entity) injection", file_path))

    if re.search(r'<!DOCTYPE[^>]*\[', content, re.IGNORECASE):
        bugs.append(("DOCTYPE with internal subset — possible XXE vector", file_path))

    return bugs


def scan_sql_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    bugs = []

    if re.search(r"(SELECT|INSERT|UPDATE|DELETE)[^;]*['\"`]\s*\+", content, re.IGNORECASE):
        bugs.append(("Potential SQL injection (string concatenation in query)", file_path))

    if re.search(r'GRANT\s+ALL\s+PRIVILEGES', content, re.IGNORECASE):
        bugs.append(("Overly permissive GRANT (GRANT ALL PRIVILEGES)", file_path))

    if re.search(r'\b(password|passwd)\s*=\s*["\'][^"\']{3,}["\']', content, re.IGNORECASE):
        bugs.append(("Hardcoded password in SQL file", file_path))

    return bugs
