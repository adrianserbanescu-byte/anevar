// Service worker (Manifest V3). Face POST-ul la aplicația locală din contextul extensiei,
// care are host_permissions pe 127.0.0.1:8000 -> fetch fără restricții CORS de pagină.
const APP = "http://127.0.0.1:8000";

chrome.runtime.onInstalled.addListener(() => {
  console.log("Import anunț → Evaluare ANEVAR instalat.");
});

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg && msg.type === "import-anunt") {
    fetch(APP + "/api/import-anunt", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ html: msg.html, url: msg.url }),
    })
      .then(async (r) => {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then((data) => sendResponse({ ok: true, data }))
      .catch((e) => sendResponse({ ok: false, error: String(e && e.message || e) }));
    return true; // răspuns asincron
  }
  if (msg && msg.type === "ping-app") {
    fetch(APP + "/api/status")
      .then(async (r) => sendResponse({ ok: r.ok, data: r.ok ? await r.json() : null }))
      .catch(() => sendResponse({ ok: false }));
    return true;
  }
});
