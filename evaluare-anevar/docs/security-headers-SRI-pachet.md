# Pachet security-headers + SRI MapLibre — gata de implementat

> Răspunde la findings-urile C & D (audituri pre-lansare): **0 headere de securitate** + **MapLibre din CDN
> fără SRI**. Acesta e un pachet **copy-paste-ready** pentru cine implementează — eu (E) raportez, **nu aplic fix**.
> Toate valorile (hash-uri SRI, CSP) sunt verificate online azi (2026-06-10). ⚠️ DRAFT — testați harta după aplicare.

---

## Partea A — SRI pentru MapLibre (dacă rămâne pe CDN)

Hash-uri **SHA-384 calculate azi** pe fișierele exacte `maplibre-gl@4.7.1` de pe unpkg (js=803086 B, css=65534 B):

Înlocuire în `evaluare-anevar/src/evaluare/web/templates/descoperire.html` (L8–L11):
```html
<link rel="stylesheet" href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css"
      integrity="sha384-MinO0mNliZ3vwppuPOUnGa+iq619pfMhLVUXfC4LHwSCvF9H+6P/KO4Q7qBOYV5V"
      crossorigin="anonymous"
      onerror="window.__harta_indisponibila=true">
<script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"
        integrity="sha384-SYKAG6cglRMN0RVvhNeBY0r3FYKNOJtznwA0v7B5Vp9tr31xAHsZC0DqkQ/pZDmj"
        crossorigin="anonymous"
        onerror="window.__harta_indisponibila=true"></script>
```
- `crossorigin="anonymous"` e **obligatoriu** alături de `integrity` (altfel browserul nu validează).
- `onerror` existent rămâne — dacă hash-ul nu se potrivește (CDN compromis), scriptul **NU se execută** → degradare grațioasă la „hartă indisponibilă", exact ca acum la lipsa de net.

### ⚠️ Recomandare mai bună (C deja a oferit): bundle MapLibre LOCAL
App-ul e `.exe` offline-distribuit → best-practice desktop = **zero CDN**. Bundling-ul `maplibre-gl@4.7.1` în `static/`
rezolvă SIMULTAN: (1) supply-chain (unpkg compromis → JS arbitrar în pagină cu PII din localStorage) și (2) reziliență.
**`descoperire.html` e zona lui C** → bundling-ul îi revine lui C; SRI-ul de mai sus e doar varianta interimară dacă rămâne CDN.
> Notă: chiar bund-uit local, harta tot cheamă `tiles.openfreemap.org` pentru tile-uri (vezi CSP mai jos) — rămâne o dependență de net la runtime pe pagina de descoperire (care oricum e online-only).

---

## Partea B — Security headers (middleware FastAPI)

**Punct de inserție perfect, deja existent:** middleware-ul `doar_host_local` din
`evaluare-anevar/src/evaluare/web/app.py` (L45–67) deja setează `Cache-Control` pe răspuns. Se adaugă headerele acolo,
**chiar înainte de `return resp`** (L67):

```python
        # --- Security headers (defense-in-depth; audit C/D pre-lansare) ---
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        resp.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=()"
        resp.headers.pop("server", None)          # ascunde fingerprint-ul „uvicorn" (finding D)
        if "text/html" in (resp.headers.get("content-type") or ""):
            resp.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' https://unpkg.com 'unsafe-inline'; "
                "style-src 'self' https://unpkg.com 'unsafe-inline'; "
                "img-src 'self' data: https://tiles.openfreemap.org; "
                "connect-src 'self' https://tiles.openfreemap.org; "
                "worker-src blob:; "
                "font-src 'self' data:; "
                "object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
            )
```
(Suplimentar, pentru a elimina complet header-ul Server, pornește uvicorn cu `server_header=False` în `uvicorn.run(...)`.)

### De ce exact acest CSP (altfel rupe harta)
| Directivă | Motiv |
|---|---|
| `script-src … https://unpkg.com` | încărcarea MapLibre de pe unpkg (scoate-l dacă bundle-uiești local) |
| `worker-src blob:` | **gotcha MapLibre** — creează web-workers din `blob:`; fără asta harta NU pornește |
| `connect-src … https://tiles.openfreemap.org` | `fetch` style JSON (`/styles/liberty`) + vector tiles (descoperire.html:388) |
| `img-src … data: https://tiles.openfreemap.org` | sprites/icoane hartă + `data:` URI |
| `'unsafe-inline'` (script+style) | app-ul are **mult JS/CSS inline** în template-uri (`{% include "_design.css" %}`, `<script>` inline). E un compromis: CSP rămâne al 4-lea strat anti-XSS (peste `escapeHtml`+`urlSafe`+teste), dar `'unsafe-inline'` slăbește `script-src`. **Upgrade viitor (lane C):** nonce-uri per-request → se poate scoate `'unsafe-inline'`. |

`X-Frame-Options: DENY` + `frame-ancestors 'none'` = anti-clickjacking (redundant intenționat: headerul pt browsere vechi, CSP pt cele noi). `nosniff` = quick-win anti MIME-sniffing.

### Verificare după aplicare
1. Pornește app-ul, deschide **/descoperire**, confirmă că **harta se încarcă** (dacă apare goală → verifică în consolă erori CSP pe `worker-src`/`connect-src`).
2. `curl -I http://127.0.0.1:8000/` → confirmă cele 5 headere + lipsa `Server`.
3. Rulează smoke-ul existent pe toate paginile (nimic să nu se rupă de la CSP).

---

## Prioritate & owner (recomandare — decizia rămâne a ta)
| Acțiune | Owner sugerat | Efort |
|---|---|---|
| SRI MapLibre (interimar) **sau** bundle local | **C** (`descoperire.html`/static) | mic / mediu |
| Middleware security-headers + CSP | **A** (`app.py`) | mic (~12 linii în middleware existent) |
| `server_header=False` la uvicorn.run | A | 1 linie |

**Zero fix aplicat de mine.** Hash-urile SRI sunt valabile cât timp versiunea rămâne `4.7.1` (fișiere imutabile pe unpkg).
