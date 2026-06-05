// Verifică dacă aplicația locală răspunde și afișează starea.
const el = document.getElementById("status");
chrome.runtime.sendMessage({ type: "ping-app" }, (resp) => {
  if (chrome.runtime.lastError || !resp || !resp.ok) {
    el.className = "status ko";
    el.textContent = "✗ Aplicația nu rulează (127.0.0.1:8000)";
  } else {
    el.className = "status ok";
    el.textContent = "✓ Aplicația rulează — gata de import";
  }
});
