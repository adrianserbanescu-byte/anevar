# Brief Lovable — rută nouă „Fluxul livrabilelor" (repo `anevar-ui-concept`)

> **Țintă:** proiectul Lovable `anevar-ui-concept`
> (https://lovable.dev/projects/afa6321f-0cf0-4d97-be9a-29ffeda67216,
> repo `adrianserbanescu-byte/anevar-ui-concept`, stack TanStack Start + React + Radix + Tailwind).
> Adaugă **o rută nouă** `flux-livrabile`, lângă cele existente (`index`, `aml`, `grila`, `descoperire`,
> `evaluare.$id`, `formular`). Arhitectura reflectată = **LOCAL** (cont local, fără server).

---

## ⚙️ Cum se integrează (de ce contează ce ceri)

Repo-ul Lovable e **laboratorul de concept vizual** (React/Tailwind — corect așa). Produsul real e
**FastAPI + Jinja2 + vanilla JS, `.exe` offline**. Eu NU copiez codul React; **portez design-language-ul**
(tokeni + look-ul componentelor) în `templates/_design.css`. Ca să fie portabil 100%:

1. ✅ **Refolosește tokenii de marcă DEJA existenți** în `src/styles.css` — NU adăuga paletă nouă:
   `--color-parchment`, `--color-parchment-deep`, `--color-ink`, `--color-ink-soft`,
   `--color-sienna`, `--color-sienna-deep`, `--color-cadastral` (verde), `--color-brass`,
   `--color-tricolor-blue/-yellow/-red`, plus `--font-serif/-sans/-mono`.
2. ✅ **Fonturi DOAR de sistem** (deja așa în repo: serif Constantia/Cambria, sans Segoe UI, mono Consolas).
   FĂRĂ Google Fonts / CDN — aplicația finală e offline.
3. ✅ **Refolosește componenta `Shell`** (`src/components/concept/Shell.tsx`) pentru antet/cadru, ca
   ruta nouă să arate identic cu restul conceptului.
4. ✅ Stil sobru, „registru cadastral / topograf" — consistent cu rutele existente. Fără efecte SaaS colorate.

### Codarea celor 3 niveluri legale → mapează pe tokenii existenți
| Nivel | Înțeles | Token |
|-------|---------|-------|
| **Nivel 1 · Firmă** | document de firmă, o singură dată | `--color-tricolor-blue` (sau `--color-ink`) |
| **Nivel 2 · Client/dosar** | per client | `--color-sienna` |
| **Nivel 3 · Eveniment** | condiționat (RTN/RTS) | `--color-destructive` |
| **„pregătit"** | output gata | `--color-cadastral` (verde) |
| **progres / sigiliu** | bară, badge | `--color-brass` |

---

## 🧩 Prompt de pus în Lovable (copiază blocul)

```
Adaugă o rută nouă „flux-livrabile” în acest proiect (anevar-ui-concept), refolosind
componenta Shell și tokenii de marcă existenți din styles.css (parchment, ink, sienna,
cadastral, brass, tricolor) și fonturile de sistem deja definite. NU introduce paletă
sau fonturi noi. Estetica: registru cadastral / topograf, ca restul conceptului.

Ecranul prezintă „Fluxul livrabilelor unei evaluări imobiliare ANEVAR” — harta a ceea ce
produce un dosar, pe 3 niveluri legale. Arhitectură LOCALĂ (cont local, fără server).

STRUCTURĂ:
1) Sus — un STEPPER orizontal cu 7 pași numerotați, clickabili, cu stări (făcut ✓ / activ /
   următor): 0 Cont · 1 Dosar · 2 Proprietate · 3 Calcul · 4 Conformitate · 5 Asumare ·
   6 Predare. Pasul 0 colorat cu nuanța „firmă” (tricolor-blue/ink).
2) Stânga — un „dosar” cu colț îndoit care arată ecranul pasului activ (vezi cele 7 ecrane).
3) Dreapta — un DOCK sticky de livrabile: antet întunecat (ink) cu titlu + contor
   „X din N pregătite” + bară de progres brass; apoi 5 grupuri (vezi mai jos). Fiecare
   item se aprinde verde-cadastral („pregătit”) când pasul care îl produce e atins.

Folosește componentele Radix existente (tabs/switch/checkbox/progress) pentru
interactivitate vanilla (doar comutare de pas/stare — fără logică de business).
```

---

## 🗺️ Cele 7 ecrane de pas (mockup)

| # | Pas | Nivel | Conținut |
|---|-----|-------|----------|
| **0** | **Cont evaluator** | 🔵 Firmă | Comutator **PFA / PJ**. 3 pastile-document de firmă: *Norme interne · Decizie de desemnare · Politică GDPR*. La PFA, „Decizie de desemnare" = tăiată „scutit (N. art. 7)". Notă: „o singură dată, revizuite la modificări legislative". |
| **1** | **Deschidere dosar** | — | 5 carduri-opțiune: *Dosar nou · Import .docx · Din extensia browser · Din ingestie PDF · Din dosar existent*. Sub: identitate (tip × scop → profil → ghid GEV 520). |
| **2** | **Date proprietate** | — | Câmpuri: adresă, cadastral/CF, **drept evaluat, sarcini CF, regim teren, regim urbanistic, utilități, cale de acces**. Alertă: la garantare sunt obligatorii (SEV 230 / GEV 630). |
| **3** | **Comparabile & calcul** | — | Pastile 3 grile (casă/teren/chirii) + 3 abordări (cost/comparație/venit) → reconciliere. Card „135.267 EUR (fără TVA)". Alertă ajustare brută >25% (GEV 520). |
| **4** | **Client & conformitate** | 🟫 Client + 🟥 Eveniment | KYC (tip client, PEP, beneficiar real, risc relație). 2 **switch-uri de eveniment**: „numerar ≥ 10.000 € → RTN" și „suspiciune → RTS". Avertisment: app NU verifică automat sancțiuni/PEP; documente = drafturi (jurist). |
| **5** | **Asumarea răspunderii** | — | Checkbox mare care **blochează** „Generează raportul" până e bifat. Text: numerele = deterministe, proza [AI] = răspunderea evaluatorului. |
| **6** | **Generare & predare** | — | 4 carduri-pachet (Raport · Conformitate firmă · Conformitate client · Audit) + butoane „Descarcă pachetul" / „Backup .zip". |

---

## 📦 Dock-ul de livrabile — 5 grupuri

1. **Nivel 1 · Firmă (cont)** — `o singură dată` — 🔵
   Norme interne · Decizie de desemnare *(scutit la PFA)* · Politică de prelucrare GDPR
2. **Raport de evaluare** — `per dosar` — 🟡
   Raport `.docx` (SEV 106 / GEV 520, cu Anexe foto+scanuri)
3. **Nivel 2 · Client / dosar** — `la fiecare client` — 🟫
   Fișă KYC · Evaluare risc (relație) · Acord de consimțământ
   ⚠️ **Notă de informare GDPR** — item-avertisment punctat roșu, status „lipsește (art. 22(2))" *(gol de conformitate real — NU verde)*
4. **Nivel 3 · Eveniment** — `doar dacă apare` — 🟥
   RTN · RTS — implicit status „condiționat"
5. **Trasabilitate** — `per dosar`
   Urma de audit · Backup dosare `.zip`

**Stări item:** `în așteptare` → `pregătit` (verde+bifă) · `neaplicabil` (hașurat, PFA-decizie) ·
`condiționat` (Nivel 3 inactiv) · `lipsește` (roșu punctat — doar nota GDPR).

---

## 📥 Ce fac cu rezultatul
Iau tokenii/stilurile componentelor noi (stepper, dock, carduri-pas, pastile de nivel, badge-uri de
stare) și le port în `templates/_design.css`; adaptez șabloanele Jinja. Produsul rămâne `.exe` offline,
server-rendered. Referință de logică: prototipul `docs/ux-flow/flow-livrabile.html` (aceeași structură).

## 🔭 Viitor (NU desena acum)
La trecerea „firmă pe server": Nivel 1 → server (partajat, fără PII client → GDPR ușor); Nivel 2/3 rămân
local. S-ar adăuga un „Pas −1 · Firmă (server)" înaintea contului. Deocamdată: tot local.
