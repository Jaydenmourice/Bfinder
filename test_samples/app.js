// User authentication and dashboard logic

const apiKey = "sk-live-abc123secretXYZ987";       // hardcoded secret
const token  = "eyJhbGciOiJIUzI1NiIsInR5cCI6";    // hardcoded token

// Debug leftover
console.log("App loaded, token:", token);

// --- XSS via innerHTML assignment ---
function renderUsername(name) {
    document.getElementById("user").innerHTML = name;   // innerHTML =
}

// --- XSS via outerHTML ---
function replaceCard(html) {
    document.querySelector(".card").outerHTML = html;   // outerHTML =
}

// --- XSS via insertAdjacentHTML ---
function appendMessage(msg) {
    document.getElementById("chat").insertAdjacentHTML("beforeend", msg);
}

// --- eval usage ---
function runUserScript(code) {
    eval(code);
}

// --- document.write ---
function writeContent(data) {
    document.write(data);
}

// --- Infinite loop ---
function pollServer() {
    while (true) {
        fetchUpdates();
    }
}

// --- Insecure direct object reference (dynamic window key) ---
function getModule(name) {
    return window[name];
}

// --- CORS with credentials ---
function sendCreds(url, data) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url);
    XMLHttpRequest.withCredentials = true;
    xhr.send(data);
}

// --- Unvalidated URL params ---
function getRedirect() {
    var next = location.search;
    var hash = location.hash;
    return next || hash;
}

// --- Insecure cookie ---
function setSession(sid) {
    document.cookie = "session=" + sid;
}

// --- localStorage with sensitive data ---
function cacheUser(user) {
    localStorage["userData"] = JSON.stringify(user);
}

// --- Deprecated library import ---
const $ = require('jquery');

// --- Browser fingerprinting APIs ---
function collectDeviceInfo() {
    return {
        ua:     navigator.userAgent,
        cores:  navigator.hardwareConcurrency,
        mem:    navigator.deviceMemory,
        sw:     screen.width,
        sh:     screen.height,
        ref:    document.referrer,
    };
}

// --- Insecure randomness ---
function generateToken() {
    return Math.random().toString(36).slice(2);
}

// --- Client-side encryption (key in source) ---
const encrypted = CryptoJS.AES.encrypt("secret", "hardcodedKey");

// --- WebSocket without origin check ---
const ws = new WebSocket("ws://api.example.com/live");

// --- Geolocation ---
function getLocation() {
    navigator.geolocation.getCurrentPosition(pos => console.log(pos));
}

// --- FileReader ---
function readFile(f) {
    const reader = new FileReader();
    reader.readAsText(f);
}

// --- postMessage sender and listener (both sides) ---
window.postMessage({ action: "login" }, "*");
window.addEventListener('message', function(event) {
    processMessage(event.data);     // no origin check
});

// --- React dangerouslySetInnerHTML ---
function RawHTML({ html }) {
    return <div dangerouslySetInnerHTML={{ __html: html }} />;
}

// --- setTimeout with string (eval-equivalent) ---
setTimeout("window.location = '/logout'", 3000);

// --- Insecure HTTP fetch ---
fetch("http://api.example.com/data")
    .then(r => r.json())
    .then(d => console.log(d));

// --- Prototype pollution ---
function merge(obj, payload) {
    obj.__proto__ = payload;
    constructor.prototype.isAdmin = true;
}
