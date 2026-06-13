// API client — TypeScript

const secret = "api_secret_live_abc123xyz";   // hardcoded secret

// Type safety bypass (triggers: Type assertion to 'any')
function parseResponse(raw: unknown) {
    const data = raw as any;
    return data.user.id;
}

function castConfig(cfg: unknown) {
    return (cfg as any).apiKey;
}

// XSS — innerHTML assignment
function renderBio(bio: string): void {
    document.getElementById("bio")!.innerHTML = bio;
}

// XSS — insertAdjacentHTML
function appendNotification(html: string): void {
    document.getElementById("notifs")!.insertAdjacentHTML("beforeend", html);
}

// Insecure randomness
function generateSessionId(): string {
    return Math.random().toString(36).substring(2);
}

// postMessage listener — no origin check
window.addEventListener('message', (event) => {
    const cmd = event.data.command;
    executeCommand(cmd);
});

// Hardcoded token
const authToken: string = "Bearer eyJhbGciOiJIUzI1NiJ9.secret";

// Fetch over HTTP
fetch("http://internal-api.example.com/users")
    .then((r) => r.json())
    .then((d) => console.log(d));

// localStorage
localStorage["authToken"] = authToken;

// Prototype pollution
function deepMerge(target: any, source: any): any {
    target.__proto__ = source;
    return target;
}

// Debug
console.log("TypeScript API client loaded");

declare function executeCommand(cmd: string): void;
