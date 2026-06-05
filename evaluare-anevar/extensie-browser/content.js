// Content script: injectează un buton pe pagina de anunț. Omul navighează manual;
// la apăsare, trimite HTML-ul paginii curente către aplicația locală (zero scraping).
(function () {
  const APP = "http://127.0.0.1:8000/api/import-anunt";

  const btn = document.createElement("button");
  btn.textContent = "➕ Trimite în Evaluare ANEVAR";
  Object.assign(btn.style, {
    position: "fixed", right: "16px", bottom: "16px", zIndex: 999999,
    padding: "10px 16px", background: "#9d4a25", color: "#fff", border: "0",
    borderRadius: "6px", font: "600 14px Segoe UI, sans-serif", cursor: "pointer",
    boxShadow: "0 4px 14px rgba(0,0,0,.25)",
  });
  btn.addEventListener("click", async () => {
    btn.textContent = "Se trimite…";
    try {
      const r = await fetch(APP, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ html: document.documentElement.outerHTML, url: location.href }),
      });
      if (!r.ok) throw new Error("HTTP " + r.status);
      const d = await r.json();
      btn.textContent = `✓ ${d.pret || "?"} ${d.moneda || ""} · ${d.suprafata || "?"} mp`;
    } catch (e) {
      btn.textContent = "✗ Pornește aplicația (127.0.0.1:8000)";
      console.warn("Import ANEVAR:", e);
    }
    setTimeout(() => (btn.textContent = "➕ Trimite în Evaluare ANEVAR"), 4000);
  });
  document.body.appendChild(btn);
})();
