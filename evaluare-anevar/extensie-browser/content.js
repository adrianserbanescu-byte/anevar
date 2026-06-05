// Content script — Import anunț → Evaluare ANEVAR
// Omul navighează MANUAL pe storia.ro / imobiliare.ro (utilizare normală a site-ului).
// La apăsarea butonului, trimitem HTML-ul paginii curente către service worker, care îl
// POST-ează la aplicația locală. Zero scraping automat, zero polling, zero anti-bot.
(function () {
  "use strict";
  if (window.__anevarInjectat) return;        // idempotent (SPA poate re-rula scriptul)
  window.__anevarInjectat = true;

  const SIENNA = "#9d4a25";

  // ── Detectează dacă pagina curentă e un ANUNȚ (nu listă/căutare/home) ──────────
  function estePaginaAnunt() {
    const p = location.pathname;
    // storia.ro: anunțurile sunt la /ro/oferta/... ; imobiliare.ro: detaliul are un ID -X<digits>
    if (location.hostname.includes("storia.ro")) return /\/oferta\//.test(p);
    if (location.hostname.includes("olx.ro")) return /\/d\/oferta\//.test(p);
    if (location.hostname.includes("imobiliare.ro"))
      return /-[0-9a-f]{6,}$|\/(vanzare|inchiriere)-/i.test(p) && !/lista|cauta|rezultate/i.test(p);
    return true;
  }

  // ── UI: buton flotant + panou de rezultat ────────────────────────────────────
  const wrap = document.createElement("div");
  Object.assign(wrap.style, {
    position: "fixed", right: "16px", bottom: "16px", zIndex: 2147483647,
    font: "14px Segoe UI, system-ui, sans-serif",
  });

  const btn = document.createElement("button");
  btn.textContent = "➕ Trimite în Evaluare ANEVAR";
  Object.assign(btn.style, {
    padding: "11px 16px", background: SIENNA, color: "#fff", border: "0",
    borderRadius: "8px", fontWeight: "600", cursor: "pointer",
    boxShadow: "0 6px 18px rgba(0,0,0,.28)",
  });
  btn.setAttribute("aria-label", "Trimite anunțul curent în aplicația Evaluare ANEVAR");

  const panou = document.createElement("div");
  Object.assign(panou.style, {
    display: "none", marginBottom: "10px", maxWidth: "320px", padding: "12px 14px",
    background: "#fbf7ef", color: "#2a2118", border: "1px solid " + SIENNA,
    borderRadius: "8px", boxShadow: "0 6px 18px rgba(0,0,0,.22)", lineHeight: "1.45",
  });

  wrap.appendChild(panou);
  wrap.appendChild(btn);

  function rand(d) {
    const linii = [];
    if (d.titlu) linii.push(`<b>${esc(d.titlu).slice(0, 90)}</b>`);
    const pm = (d.pret && d.suprafata)
      ? Math.round(parseFloat(d.pret) / parseFloat(d.suprafata)) + " €/mp" : "";
    linii.push(
      `💶 <b>${d.pret ? esc(d.pret) + " " + esc(d.moneda || "EUR") : "preț ?"}</b>` +
      ` · 📐 ${d.suprafata ? esc(d.suprafata) + " mp" : "supr. ?"}` +
      (d.suprafata_teren ? ` · teren ${esc(d.suprafata_teren)} mp` : "") +
      (pm ? ` · <b>${pm}</b>` : "")
    );
    const sec = [d.an ? "an " + d.an : "", d.material || "", d.incalzire || "",
                 d.nr_camere ? d.nr_camere + " camere" : ""].filter(Boolean).join(" · ");
    if (sec) linii.push(`<span style="opacity:.8">${esc(sec)}</span>`);
    linii.push(`<span style="color:${SIENNA}">⚠️ Preț din ofertă — aplică ajustarea ofertă→tranzacție.</span>`);
    if (d.in_coada) linii.push(`<span style="opacity:.7">În coada de import: ${d.in_coada} anunț(uri).</span>`);
    linii.push(`<a href="http://127.0.0.1:8000/descoperire" target="_blank" style="color:${SIENNA};font-weight:600">→ Deschide în aplicație</a>`);
    return linii.join("<br>");
  }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, c =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  }
  function arata(html, eroare) {
    panou.style.display = "block";
    panou.style.borderColor = eroare ? "#a12" : SIENNA;
    panou.innerHTML = html;
  }

  btn.addEventListener("click", () => {
    if (!estePaginaAnunt()) {
      arata("Aceasta nu pare o pagină de anunț. Deschide un anunț individual și reîncearcă.", true);
      return;
    }
    btn.disabled = true;
    btn.textContent = "Se trimite…";
    chrome.runtime.sendMessage(
      { type: "import-anunt", html: document.documentElement.outerHTML, url: location.href },
      (resp) => {
        btn.disabled = false;
        btn.textContent = "➕ Trimite în Evaluare ANEVAR";
        if (chrome.runtime.lastError || !resp) {
          arata("✗ Nu pot contacta extensia. Reîncarcă pagina.", true);
          return;
        }
        if (!resp.ok) {
          arata("✗ Pornește aplicația <b>Evaluare ANEVAR</b> (127.0.0.1:8000), apoi reîncearcă.<br>" +
                "<span style='opacity:.7'>" + esc(resp.error || "") + "</span>", true);
          return;
        }
        const d = resp.data;
        if (!d.pret || !d.suprafata) {
          arata("⚠️ Nu am găsit preț + suprafață pe această pagină. Verifică că e un anunț de " +
                "vânzare casă/apartament și reîncearcă, sau completează manual în aplicație.", true);
          return;
        }
        arata(rand(d), false);
      }
    );
  });

  document.body.appendChild(wrap);
})();
