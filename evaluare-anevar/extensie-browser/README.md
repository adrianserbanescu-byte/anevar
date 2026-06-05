# Extensie de browser — Import anunț → Evaluare ANEVAR

Extensie completă (Manifest V3) pentru migrarea descoperirii de comparabile de la
scraping în backend la **import controlat de om**. Țintește portaluri reale: **storia.ro**
(date structurate `__NEXT_DATA__`, extragere robustă) și **imobiliare.ro**.

## Cum funcționează (flux end-to-end)
1. Omul navighează **manual** pe storia.ro / imobiliare.ro — utilizare normală a site-ului.
2. Pe pagina unui anunț apare butonul **„➕ Trimite în Evaluare ANEVAR"** (jos-dreapta).
3. La apăsare, **service worker-ul** (`background.js`) face POST cu HTML-ul paginii către
   aplicația locală (`http://127.0.0.1:8000/api/import-anunt`). Fetch-ul din service worker
   are `host_permissions` pe localhost → **fără probleme CORS**.
4. Aplicația parsează HTML-ul cu parserul existent (`parse_listing_html`): preferă
   `__NEXT_DATA__` (storia) și JSON-LD (schema.org), apoi degradează grațios la regex.
5. Anunțul (dacă are preț + suprafață) intră într-o **coadă de import** in-memory
   (dedup după URL). Panoul din extensie arată câmpurile extrase.
6. În aplicație → pagina **Descoperire** → secțiunea „📥 Anunțuri importate" → bifezi →
   **„➜ Trimite bifatele la grila casă"** → ajung în grila de comparabile.

Zero scraping automat, zero polling, zero anti-bot, zero blocare IP.

## Arhitectură (de ce așa)
- **content.js** rulează în pagina portalului: detectează dacă e o pagină de anunț,
  injectează butonul + panoul, citește `document.documentElement.outerHTML` la click și îl
  trimite prin `chrome.runtime.sendMessage` către service worker.
- **background.js** (service worker) face singurul apel de rețea către aplicația locală și
  întoarce rezultatul parsat. Centralizarea fetch-ului aici evită CORS-ul de pagină și ține
  logica de rețea într-un singur loc.
- **popup.html/js** verifică dacă aplicația rulează (ping pe `/api/anunturi-importate`) și dă
  instrucțiuni + scurtătură către pagina Descoperire.

## Instalare (dezvoltare)
1. Pornește aplicația Evaluare ANEVAR (`evaluare-anevar.exe` sau `python -m evaluare`).
2. Chrome/Edge → `chrome://extensions` → activează **Developer mode** → **Load unpacked** →
   selectează folderul `extensie-browser`.
3. Deschide un anunț pe storia.ro / imobiliare.ro și apasă butonul.

## Fișiere
- `manifest.json` — declarația extensiei (portaluri + host permission pe localhost + popup).
- `content.js` — detectează pagina de anunț, injectează butonul/panoul, trimite HTML-ul.
- `background.js` — service worker: POST la aplicația locală + ping de status.
- `popup.html` / `popup.js` — status aplicație + instrucțiuni + scurtătură.
- `icon128.png` — iconița extensiei.

## Limite și avertismente (citește)
- **Oferte ≠ tranzacții.** Prețurile sunt din anunțuri; aplică ajustarea ofertă→tranzacție
  (GEV 520 §4.3.4). Aplicația marchează asta explicit pe fiecare anunț importat.
- **Respectă Termenii portalurilor.** Extensia nu automatizează navigarea și nu ocolește
  protecții — omul deschide manual fiecare anunț. Folosește pentru volume rezonabile.
- **Selectoarele se pot schimba.** storia/imobiliare își pot modifica structura; parserul
  preferă date structurate (mai stabile) și degradează grațios, dar verifică întotdeauna
  datele extrase înainte de a le folosi în raport.

## De extins (opțional)
- Publicare în Chrome Web Store (necesită cont developer + review).
- Suport pentru alte portaluri (olx.ro etc.) — adaugă host în manifest; parserul e generic.
