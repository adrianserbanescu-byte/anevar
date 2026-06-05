# Spec — Extensie de browser pentru import comparabile (înlocuiește scraping-ul)

**Scop:** specificație tehnică pentru migrarea descoperirii de comparabile de la **scraping în
backend** (fragil, risc ToS/anti-bot/GDPR) la o **extensie de browser** controlată de om.
(Punctul C6 din plan; recomandat unanim de consiliul de review.)

## De ce
Scraping-ul din backend Python:
- se sparge la schimbări de layout / protecții anti-bot (Cloudflare, CAPTCHA);
- riscă blocarea IP-ului evaluatorului și încălcarea ToS / drept sui-generis pe baze de date;
- anunțurile conțin date de contact = date personale (GDPR).

Cu o extensie, **omul navighează manual** (utilizare normală a site-ului), iar extensia doar
**citește pagina deschisă** și o trimite local. Zero scraping automat, zero anti-bot, zero IP ban.

## Arhitectură
```
Utilizator (navighează manual pe imobiliare.ro/storia.ro)
   │  apasă butonul „➕ Trimite în Evaluare ANEVAR" din extensie
   ▼
Extensia citește DOM-ul paginii curente → extrage câmpuri (preț, suprafață, an, …)
   │  POST http://127.0.0.1:8000/api/import-anunt   (aplicația rulează local)
   ▼
Aplicația validează + adaugă comparabilul în grilă (cu avertismentul „ofertă, nu tranzacție")
```

## Componente
1. **Extensie (Manifest V3, JS):**
   - `content script` per portal: selectoare pentru preț/suprafață/an/cameră/teren/încălzire.
   - buton injectat în pagină / popup.
   - `fetch("http://127.0.0.1:8000/api/import-anunt", {method:"POST", body: JSON})`.
2. **Endpoint nou în aplicație** `POST /api/import-anunt`:
   - primește JSON-ul extras, îl trece prin parserul existent (`url_parser`/`extractor`),
     îl normalizează și îl pune în coada de comparabile (localStorage/grilă).
   - acceptă CORS de la extensie (origine `chrome-extension://…`).
3. **Fallback fără extensie:** câmp „lipește textul anunțului" → LLM/parser extrage atributele
   (deja parțial suportat de infrastructura actuală).

## De decis
- Câte portaluri la lansare (imobiliare.ro, storia.ro).
- Distribuția extensiei (Chrome Web Store vs încărcare manuală „unpacked").
- Securitate: extensia trimite doar către `127.0.0.1` (nu expune date în afară).

## Efort estimat
~2–4 zile pentru o extensie funcțională pe 2 portaluri + endpoint-ul local. Scraping-ul backend
rămâne ca fallback „best-effort" cu disclaimer (deja afișat).
