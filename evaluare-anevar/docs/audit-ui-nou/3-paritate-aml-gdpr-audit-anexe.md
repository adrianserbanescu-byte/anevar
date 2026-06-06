# Audit funcțional de paritate — tab-urile AML / GDPR / Audit / Anexe (UI nou vs. funcționalitate reală)

Scop: owner-ul cere ca sub-tab-urile AML/GDPR/Audit din UI-ul nou (`curent/dosar.html`) să **reconstruiască in-place** aceleași opțiuni ca paginile spre care fac acum redirect — **fără** a mai trimite la pagina veche. Iar **Anexe** trebuie să devină sub-tab al **Raportului**, **ÎNAINTE** de „Generează" (fiindcă pozele/scanurile intră chiar în raport).

Surse verificate (absolut):
- UI nou: `src/evaluare/web/templates/curent/dosar.html` (tab-uri `p-aml`, `p-gdpr`, `p-audit`, `p-anexe`)
- AML: `src/evaluare/web/templates/aml.html` + `src/evaluare/web/routers/aml.py` + `src/evaluare/aml/{serviciu,risc,indicatori,documente,raportare,store,liste,incadrare}.py`
- GDPR: `src/evaluare/gdpr/documente.py` (+ endpoint-uri în `aml.py`)
- Audit: `src/evaluare/audit/{jurnal,raport_audit,snapshot,validare_x}.py` + `src/evaluare/web/routers/evaluare.py` (`/api/evaluare/{eid}/audit.txt`) + `curent.py`
- Anexe: `src/evaluare/report/generator.py` (`_adauga_anexe`, `_decode_foto`) + `src/evaluare/assembler.py` (`EvaluationInput.photos/documente`) + `wizard.html` (upload vechi)

**Verdict global: toate 4 tab-urile din UI nou conțin DOAR text/linkuri.** Niciun câmp, niciun buton funcțional, niciun upload. Backend-ul însă suportă deja integral AML, GDPR și Anexe (foto+scanuri); doar urma de audit per-dosar lipsește pe fluxul nou (pe foldere).

---

## Stadiul actual al celor 4 tab-uri (UI nou) — dovadă

`dosar.html`, liniile 141–150, conțin exclusiv `<p class="hint">` cu linkuri/​text:
- `p-aml` (l.141–142): „Modulul AML (risc + documente): **deschide AML ↗**" → link `target="_blank"` la `/aml`.
- `p-gdpr` (l.143–146): 3 linkuri (`/aml`, `/documente/politica-confidentialitate`, `/documente/disclaimer-profesional`).
- `p-audit` (l.147–148): text „Urma de audit se descarcă după calcul (în versiunea comercială)…" + link `/documente/evaluare-juridica`. **Niciun buton.**
- `p-anexe` (l.149–150): text „Atașarea fișierelor vine cu versiunea comercială…". **Afirmație incorectă** — vezi secțiunea Anexe.

---

## 1) Tab AML

Tabul nou = **doar link** la `/aml`. Pagina `/aml` (servită de `aml.py::pagina_aml`) are funcționalitate completă, toată pe API-uri care există deja și pot fi apelate identic dintr-un sub-tab.

| Funcție (pagina veche / backend) | În sub-tabul UI nou? | Dovadă | Ce trebuie reconstruit in-place |
|---|---|---|---|
| Tip entitate evaluator (PFA/PJ) → declanșează „persoană desemnată" | ❌ | `aml.html` l.25–29; logică `incadrare.necesita_persoana_desemnata` | `<select id=tip_entitate>` cu 2 opțiuni |
| KYC client: tip PF/PJ, nume, prenume, CNP; PJ: denumire, CUI | ❌ | `aml.html` l.35–50 | câmpurile + toggle `#pj` la `tip_client==PJ` |
| Beneficiar real (>25%) — colectat pt fișa KYC | 🟡 (parțial backend) | `_client` JS l.91–93 trimite 1 beneficiar; `documente.genereaza_fisa_kyc` listează `beneficiari_reali` | câmp beneficiar real în formular (azi doar nume/prenume din PF) |
| PEP (client/beneficiar real expus public) | ❌ | `aml.html` l.45 `#pep` | checkbox PEP |
| Semnale de risc (4): țară risc înalt, listă sancțiuni, tranzacție complexă, relație la distanță | ❌ | `aml.html` l.55–60; `risc.Semnale` | 4 checkbox-uri `#tara_risc_inalt` etc. |
| Indicatori de suspiciune (10, HCD 58 art. 6(10)) | ❌ | `aml.html` l.64–75; `indicatori.SemnaleIndicatori`, `propune_rts` | 10 checkbox-uri `.ind` |
| „Evaluează relația" → scor risc, categorie, măsuri, motive, indicatori activi, screening pe liste demonstrative, propunere RTS | ❌ | `aml.html` l.77/101–122; `POST /api/aml/evalueaza` → `serviciu.evalueaza_relatie` | buton + `fetch('/api/aml/evalueaza')` + randare rezultat (badge categorie, listă documente) |
| Generare documente .docx: norme interne, evaluare risc, fișă KYC, decizie desemnare, RTS, RTN | ❌ | `aml.py` l.50–101 (6 endpoint-uri); `aml.html` l.116–119, 123–139 | butoane per-document → `POST /api/aml/<doc>.docx` + descărcare blob |
| Avertisment legal RTS/RTN (confirm() — art. 33 tipping-off) | ❌ | `aml.html` l.124–130 | reluat la butonul RTS/RTN |
| Avertisment „NU verifică automat sancțiuni/PEP" + surse oficiale (OpenSanctions/EU/OFAC) | ❌ | `aml.html` l.13–20 | bloc `.avert-legal` reluat în sub-tab |

Concluzie AML: **backend 100% gata** (toate endpoint-urile există). De portat doar **frontend-ul** din `aml.html` (formular + JS `evalueaza()`/`descarca()`) în panoul `p-aml`, ajustând doar avertismentul/aria-urile. **0 cod backend nou.**

---

## 2) Tab GDPR

Tabul nou = **doar linkuri**. Funcționalitatea reală GDPR sunt 2 generatoare .docx, deja expuse ca endpoint-uri (folosite azi din pagina `/aml`, fieldset „Documente GDPR").

| Funcție (pagina veche / backend) | În sub-tabul UI nou? | Dovadă | Ce trebuie reconstruit in-place |
|---|---|---|---|
| Politică de prelucrare a datelor (model .docx, 7 secțiuni) | ❌ (doar link) | `gdpr/documente.genereaza_politica_gdpr`; `POST /api/gdpr/politica.docx` (`aml.py` l.103–106); `aml.html` l.83 | buton → `POST /api/gdpr/politica.docx` + descărcare |
| Acord consimțământ client (model .docx, pre-completabil nume/adresă) | 🟡 | `genereaza_consimtamant_gdpr(client_nume, adresa)` acceptă prefill; `POST /api/gdpr/consimtamant.docx` (`aml.py` l.108–111); `aml.html` l.84 | buton → endpoint; **îmbunătățire**: trimite `client_nume`/`adresa` din câmpurile dosarului (azi endpoint-ul nu primește body util — prefill neexploatat) |
| Disclaimer „operatorul de date e evaluatorul, nu aplicația" | 🟡 | `_DISCLAIMER` în .docx; în UI vechi doar ca hint | text scurt în sub-tab |
| Politica de confidențialitate / Disclaimer profesional (pagini documentare) | ✅ (există ca pagini) | `dosar.html` l.145–146 linkuri `/documente/...` | pot rămâne ca linkuri „citește" SAU randate inline; nu sunt funcții, ci documente statice |

Concluzie GDPR: **backend gata** (2 endpoint-uri). De adăugat 2 butoane in-place (ca în `aml.html` l.83–84). Opțional: pre-completare consimțământ din identitatea dosarului (necesită ca endpoint-ul `/api/gdpr/consimtamant.docx` să citească `client_nume`/`adresa` din body — mică ajustare backend, nu obligatorie pentru paritate).

---

## 3) Tab Audit

Tabul nou = **doar text** („se descarcă după calcul, versiunea comercială"). Aici e singurul **gol real de backend pe fluxul nou**.

| Funcție (pagina veche / backend) | În sub-tabul UI nou? | Dovadă | Ce trebuie reconstruit in-place |
|---|---|---|---|
| Urmă de audit per-dosar (.txt): identificare, input proprietate (hash), comparabile, rezultate piață/cost/teren, valoare finală, validări încrucișate + verdict integritate lanț | ❌ pe flux nou | Implementat DOAR pe fluxul vechi SQLite: `GET /api/evaluare/{eid}/audit.txt` (`evaluare.py` l.99–129). `curent.py` (fluxul pe foldere) **NU** are echivalent | endpoint nou `GET /api/dosar/{uid}/audit.txt` care reconstruiește `JurnalAudit` din contextul calculat (refolosind `jurnal.py` + `raport_audit.text_audit` + `validare_x.valideaza_incrucisat`, deja existente) + buton „Descarcă urma de audit" |
| Motor jurnal append-only înlănțuit prin hash, tamper-evident (`verifica()`) | ✅ backend există | `audit/jurnal.py` (complet, testat) | nimic — doar de apelat din endpoint nou |
| Validare încrucișată (audit) | ✅ backend există | `audit/validare_x.valideaza_incrucisat` (apelat în `evaluare.py`) | de inclus în urma per-dosar |
| Snapshot/hash input | ✅ backend există | `audit/snapshot.py` | refolosit de endpoint |

Concluzie Audit: **motorul există integral** (jurnal hash-înlănțuit + raport text + validare încrucișată). Lipsește **wiring-ul** pe fluxul pe foldere: un `GET /api/dosar/{uid}/audit.txt` (analog cu cel din `evaluare.py`, dar reconstruind contextul din payload-ul de calcul) + buton în `p-audit`. Efort mic; nu necesită motor nou.

---

## 4) Tab Anexe — și mutarea sub Raport (ÎNAINTE de „Generează")

Textul actual din `p-anexe` („atașarea fișierelor vine cu versiunea comercială") este **incorect**. Backend-ul suportă deja foto + scanuri, iar UI-ul **vechi** (`wizard.html`) avea upload funcțional.

| Funcție (pagina veche / backend) | În sub-tabul UI nou? | Dovadă | Ce trebuie reconstruit in-place |
|---|---|---|---|
| Câmp intrare: `EvaluationInput.photos` + `EvaluationInput.documente` (data-URL base64) | ✅ backend gata | `assembler.py` l.97–98 | doar de trimis din payload-ul `asambleaza()` (azi lipsesc cheile) |
| Embed foto în raport — „Anexa 2 — Planșe fotografice" | ✅ backend gata | `generator.py::_adauga_anexe` l.516–528 + `_decode_foto` l.491–502 (validare base64, skip fișier corupt) | nimic backend |
| Embed scanuri în raport — „Anexa 3 — Documente cadastrale/CF/acte" | ✅ backend gata | `generator.py::_adauga_anexe` l.530–542 | nimic backend |
| Upload UI: `<input type=file accept=image/* multiple>` foto + documente, preview cu ștergere, FileReader→base64, cumul în memorie (nu localStorage) | ❌ în UI nou | UI vechi: `wizard.html` l.341–350 (inputs+preview) și l.548–573 (`FOTOS`/`DOCUMENTE`, `wireUpload`, `randUpload`); payload `photos:FOTOS, documente:DOCUMENTE` (l.667–668). În UI nou, `asambleaza()` din `dosar.html` (l.252–269) **NU** include `photos`/`documente` | 2 inputs file + preview + 2 array-uri în memorie (port direct din `wizard.html`); adăugare `photos`/`documente` în obiectul `payload` din `asambleaza()` |

Fezabilitate mutare „Anexe ca sub-tab al Raportului, înainte de Generează": **DA, recomandat și ușor.**
- Raportul are deja sub-tab-urile: `Proprietate · Comparabile · Calcul · Generează` (`dosar.html` l.28–33). Se introduce **`Anexe`** ca sub-tab **între `Calcul` și `Generează`** — exact „înainte de generare", care e și ordinea logică (anexele intră în .docx la generare).
- Pozele/scanurile sunt deja parte din `EvaluationInput`, deci ajung în raport prin **același** `asambleaza()` apelat de „Calculează" și „Generează" (`dosar.html` l.270–288) — fără endpoint nou.
- Singura modificare de cod: (a) markup upload în noul sub-tab `sp-anexe`, (b) JS `wireUpload`/preview (port din `wizard.html`), (c) cele 2 chei în `payload`. **0 cod backend.**
- Tab-ul de nivel superior `Anexe` (`t-anexe`) devine redundant: fie se elimină, fie redirectează la sub-tab-ul din Raport. (Owner: anexele „n-ar trebui ca un subtab al raportului?" → **da**.)

---

## Sinteză efort (backend gata vs. de reconstruit)

| Tab | Backend | Frontend de reconstruit in-place | Cod backend nou |
|---|---|---|---|
| AML | ✅ complet (7 endpoint-uri) | Formular KYC + risc + indicatori + butoane documente (port din `aml.html`) | Nu |
| GDPR | ✅ complet (2 endpoint-uri) | 2 butoane .docx (+ opțional prefill consimțământ) | Nu (opțional: body prefill) |
| Audit | 🟡 motor există, lipsește wiring pe flux foldere | Buton „Descarcă urma de audit" | Da, mic: `GET /api/dosar/{uid}/audit.txt` |
| Anexe | ✅ complet (`photos`/`documente` + `_adauga_anexe`) | Upload foto+scanuri (port din `wizard.html`) + 2 chei în `payload`; mutat ca sub-tab al Raportului înainte de „Generează" | Nu |

---

## Rezumat (≤200 cuvinte)

Toate cele 4 tab-uri din UI-ul nou (`curent/dosar.html`, l.141–150) conțin **doar linkuri/text**, niciun câmp funcțional.

**AML** redirecționează la `/aml`, care are tot necesarul: KYC (entitate, client PF/PJ, CNP/CUI), PEP, 4 semnale de risc, 10 indicatori de suspiciune, „Evaluează relația" (scor/categorie/screening/propunere RTS) și 6 generatoare .docx (norme, evaluare risc, fișă KYC, decizie, RTS, RTN). **Backend-ul există integral** — de portat doar formularul + JS din `aml.html` in-place. **GDPR**: 2 endpoint-uri reale (`/api/gdpr/politica.docx`, `/consimtamant.docx`) — de adăugat 2 butoane (opțional prefill din dosar). **Audit**: motorul de jurnal hash-înlănțuit + validare încrucișată există (`audit/`), dar e expus doar pe fluxul vechi SQLite (`/api/evaluare/{eid}/audit.txt`); fluxul nou pe foldere (`curent.py`) **nu** are endpoint — singurul gol backend (mic: un `GET /api/dosar/{uid}/audit.txt`). **Anexe**: textul „versiune comercială" e **fals** — `EvaluationInput.photos/documente` + `_adauga_anexe` embed deja foto (Anexa 2) și scanuri (Anexa 3); UI vechi (`wizard.html`) avea upload funcțional. De portat upload-ul ca **sub-tab al Raportului, între Calcul și Generează**, plus cele 2 chei lipsă în `payload`. Fezabil, fără cod backend.
