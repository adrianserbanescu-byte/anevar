# Extensie de browser — Import anunț → Evaluare ANEVAR

Schelet funcțional (Manifest V3) pentru migrarea descoperirii de comparabile de la
scraping în backend la **import controlat de om** (vezi `../docs/spec-extensie-browser.md`).

## Cum funcționează
1. Omul navighează **manual** pe imobiliare.ro / storia.ro (utilizare normală a site-ului).
2. Pe pagina unui anunț apare butonul **„➕ Trimite în Evaluare ANEVAR"** (jos-dreapta).
3. La apăsare, extensia trimite **HTML-ul paginii curente** către aplicația locală
   (`POST http://127.0.0.1:8000/api/import-anunt`), care extrage atributele cu parserul existent.
4. Zero scraping automat, zero anti-bot, zero blocare IP.

## Instalare (dezvoltare)
1. Pornește aplicația Evaluare ANEVAR (`evaluare-anevar.exe` sau `python -m evaluare`).
2. Chrome/Edge → `chrome://extensions` → activează **Developer mode** → **Load unpacked** →
   selectează folderul `extensie-browser`.
3. Deschide un anunț și apasă butonul.

## Fișiere
- `manifest.json` — declarația extensiei (portaluri permise).
- `content.js` — injectează butonul + trimite HTML-ul la aplicația locală.
- `background.js` — service worker minimal.

## De extins
- Selectoare dedicate per portal (acum trimite tot DOM-ul; parserul aplicației extrage).
- Popup cu listă de anunțuri trimise.
- Publicare în Chrome Web Store (opțional).
