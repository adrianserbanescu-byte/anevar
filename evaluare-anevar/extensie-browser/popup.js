// Verifică dacă aplicația locală răspunde și afișează starea (versiune + coadă).
const el = document.getElementById("status");
chrome.runtime.sendMessage({ type: "ping-app" }, (resp) => {
  if (chrome.runtime.lastError || !resp || !resp.ok) {
    el.className = "status ko";
    el.textContent = "✗ Aplicația nu rulează (127.0.0.1:8000)";
    return;
  }
  el.className = "status ok";
  const s = resp.data || {};
  const v = s.versiune ? " v" + s.versiune : "";
  const n = (typeof s.anunturi_in_coada === "number")
    ? " · " + s.anunturi_in_coada + " în coadă" : "";
  el.textContent = "✓ Aplicația rulează" + v + n;
});
