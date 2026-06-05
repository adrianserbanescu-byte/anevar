# Dosar de review — Asistent de evaluare imobiliară ANEVAR

> **Scop al acestui document:** material autosuficient pentru un review independent
> („LLM council"). Reviewerul **nu are acces la cod** — tot ce contează e mai jos.
> Caut critică sinceră pe: corectitudinea metodologiei de evaluare, arhitectură,
> securitate/confidențialitate (GDPR + AML), calitatea inginerească, riscuri și
> priorități. Secțiunea finală listează întrebările pe care vreau să le adresați.

---

## 1. Rezumat executiv

Aplicație desktop **locală** (un singur `.exe`, offline) care **asistă un evaluator
autorizat ANEVAR** la întocmirea rapoartelor de evaluare imobiliară, conform
standardelor românești **SEV 2025** (transpunere a IVS) și ghidurilor **GEV**.
Automatizează partea repetitivă — calcule pe grile de comparație, descoperirea de
comparabile din anunțuri, redactarea raportului `.docx` — păstrând principiul
**„om în buclă"**: AI-ul/aplicația propun, evaluatorul decide și semnează.

- ~5.700 linii cod sursă Python + ~4.500 linii teste; **375 teste automate (verzi)**, acoperire **92%**.
- Backend FastAPI (29 rute), interfață server-rendered (Jinja), bază SQLite locală, împachetat cu PyInstaller (~176 MB).
- Module: motor de calcul, descoperire comparabile, generator raport `.docx`, modul **AML** (Legea 129/2019), ingestie PDF, audit, narativ AI.

## 2. Context, utilizator, problemă

- **Domeniu:** evaluare imobiliară pentru **garantarea creditului ipotecar** (scopul principal), dar și IFRS, asigurare, impozitare, litigiu.
- **Utilizator:** un evaluator autorizat ANEVAR (persoană fizică/PFA sau cabinet), care răspunde profesional și legal pentru raport.
- **Problema:** întocmirea unui raport conform e laborioasă (grile de ajustări, căutare comparabile, redactare standardizată, conformitate AML). Erorile de calcul/standard pot duce la respingerea raportului de bancă sau la răspundere.
- **Poziționare:** instrument de **asistență**, nu de înlocuire. Nu ia decizii de valoare în locul evaluatorului.

## 3. Ce face aplicația (pe module)

**Motor de calcul** (cele 4 abordări SEV 103/105):
- **Cost (CIN):** cost de înlocuire net segregat pe elemente (catalog IROVAL); CIN = CIB × (1−depr. fizică) × (1−funcțională) × (1−externă); depreciere fizică interpolată după vârsta cronologică ponderată. Valoare = CIN + teren.
- **Comparație teren:** grilă în 2 etape — (1) tranzacție (ajustări secvențiale/compuse: ofertă→tranzacție, drept, finanțare, condiții, condițiile pieței), (2) proprietate (ajustări aditive: localizare, acces, utilități, suprafață, urbanism…). Selecție = comparabilul cu **ajustarea brută minimă pe etapa de proprietate**. Valoare = preț/mp corectat × suprafață.
- **Comparație casă:** aceleași 2 etape dar pe **prețul total**; diferența de mărime tratată ca ajustare valorică de arie utilă (preț unitar × Δmp).
- **Venit:** capitalizare directă (VBP din grilă de chirii comparabile → venit brut potențial → NOI/rată) **și** DCF (fluxuri actualizate + valoare reziduală).
- **Reconciliere + alocare:** selecție/ponderare a abordărilor; alocare construcții = proprietate − teren.

**Descoperire comparabile:** caută anunțuri pe portaluri (imobiliare.ro/storia.ro), extrage atribute din descriere, punctează similaritatea pe 6 criterii ponderate, explică fiecare scor (referință/găsit/diferență/pondere). Comparabilele alese pot popula direct grila.

**Generator raport `.docx`:** shell SEV complet — copertă, scrisoare de transmitere, declarație de conformitate, termeni de referință (SEV 101), 7 capitole de analiză (SEV 106), alocare, risc garanție (GEV 520), anexe (surse + foto), semnătură. Raport adaptat pe **tip de proprietate** (casă+teren, apartament, comercial, industrial, agricol, special) și **scop** (garantare/IFRS/asigurare/impozitare/litigiu); ghid corect citat (GEV 520/630/500).

**Modul AML (Legea 129/2019 + Norme 37/2021 + HCD 58):** KYC (PF/PJ + beneficiar real), evaluare de risc (scor + categorie redus/standard/sporit), indicatori de suspiciune, screening pe liste (sancțiuni/PEP — momentan injectabile), prag numerar 10.000 €, generare documente (.docx): norme interne, evaluare risc, decizie desemnare, fișă KYC, RTN, RTS. Drafturile RTS/RTN se păstrează **separat** de dosar (interdicție de divulgare, art. 38).

**Auxiliare:** ingestie PDF (extras CF, CPE) cu OCR injectabil; curs BNR + Indice imobiliar ANEVAR (automate); jurnal de audit (hash-uri input, validare încrucișată); narativ AI.

## 4. Conformitate & confidențialitate

- **Standarde:** terminologie verificată față de cuprinsul SEV 2025 — SEV 101 (termeni), 102 (tipuri ale valorii), 103 (abordări), 105 (modele), 106 (documentare/raportare); GEV 520/630/500; IFRS 13. Citate explicit în raport.
- **GDPR:** datele personale (client, adresă, cadastral, CF, evaluator) sunt **anonimizate** (marcaje `[CLIENT]`, `[ADRESA]`…) **înainte** de orice apel către AI; demascarea se face local. Restul calculelor + generarea documentului — integral pe calculatorul evaluatorului.
- **AI:** narativul (text de analiză) e redactat de un LLM (Claude sau Perplexity) **doar pe baza cifrelor + text anonimizat**; evaluatorul revizuiește. Fără cheie API, raportul folosește text-șablon.
- **AML:** modulul **propune**; transmiterea efectivă la ONPCSB o face evaluatorul. Validarea juridică finală a textelor generate **nu** a fost făcută de un jurist (vezi limitări).

## 5. Arhitectură & stack

- **Limbaj:** Python 3.12. **Backend:** FastAPI (29 rute REST JSON), compus din routere pe domenii (evaluare/grile/descoperire/aml/piață/pagini) printr-un container `Deps` injectat.
- **Interfață:** **server-rendered** (șabloane Jinja + CSS + JS vanilla), nu SPA — ca să ruleze offline într-un singur `.exe`. Sistem de design unitar „registru cadastral/topograf" (un `_design.css` inclus în toate paginile; fragmente reutilizabile pentru helpere JS, busolă, cartuș, subsol).
- **Persistență:** SQLite local (dosare ca JSON + sumar). Datele se ancorează lângă `.exe`.
- **Modele de date:** Pydantic v2 (validare strictă; calcule pe `Decimal`, nu `float`).
- **Distribuție:** PyInstaller onefile, **offline** (doar fonturi de sistem, fără CDN). Rulează pe **Windows 8.1/10/11** (nu Win7).
- **AI:** SDK Anthropic / Perplexity, injectabile; client `None` → fallback la șabloane.

## 6. Calitate & inginerie

- **Teste:** 375 automate (pytest), acoperire 92%; prag de regresie `fail_under=85`. Validate pe **dosare reale** (valori de teren reproduse „la cent": Mâneciu 44.000, Brașov 78.000, Bușteni 34.000, Breaza 67.000 EUR; prețuri comparabile casă; cost CIN).
- **Tooling:** `ruff` (lint, superset pyflakes), `.pre-commit` (lint + teste), **CI GitHub Actions** (ruff + lockfile-check + pytest). Dependențe fixate cu limite superioare + `requirements.lock` (închiderea exactă; previne salturi care strică `.exe` — ex. Pillow 12 a corupt arhiva PKG).
- **Observabilitate:** logging centralizat (consolă + fișier rotativ lângă `.exe`); erorile prinse sunt acum logate (nu mai dispar tăcut). Jurnal de eroare la pornire + consola rămâne deschisă la crash.
- **Accesibilitate:** audit **WCAG 2.1 AA** trecut (contrast ≥4.5:1 text / ≥3:1 non-text verificat; focus vizibil; landmark-uri; skip-link; `prefers-reduced-motion`).
- **Decizii de proiectare documentate** (ADR): împărțirea API în routere; design system documentat.

## 7. Stare curentă

- **MVP + extensii livrate:** toate cele 4 abordări, 6 tipuri de proprietate, 5 scopuri, modul AML complet (cod), descoperire comparabile (casă + teren), wizard 5 pași, raport `.docx`, design „cadastru" complet.
- **Exemplu real:** raport pe o casă din Breaza (subiect + comparabile reale extrase de aplicație): valoare finală **135.267 EUR** (teren 27.664 · cost CIN+teren 178.735 · piață 135.267 · alocare construcții 107.603).
- **Cod pe GitHub** (privat), CI activ.

## 8. Limitări cunoscute & riscuri (declarate onest)

1. **Ajustările din grile + costurile unitare din exemple = EXEMPLU**, de confirmat de evaluator. Logica de calcul e validată; *valorile* ajustărilor sunt ilustrative.
2. **AML:** textele generate (norme, decizii, RTS/RTN) **nu au validare juridică** finală; listele de sancțiuni/PEP sunt momentan placeholder injectabil (nu live).
3. **Surse de date oficiale lipsă:** catalog IROVAL (costuri unitare), BIG (Baza Imobiliară de Garanții), ANCPI (carte funciară) — necesită acces/membru ANEVAR; momentan descoperirea se face prin scraping de portaluri (fragil la schimbări de layout, posibile probleme de ToS).
4. **Extracția LLM din anunțuri reale** e validată pe fixturi, dar nu exhaustiv pe text liber real.
5. **`.exe` nesemnat** → avertisment SmartScreen; nu rulează pe Windows 7 (Python 3.12).
6. **Single-user, fără autentificare** (instrument local) — nu e multi-utilizator/cloud.
7. **Cursul BNR / Indicele ANEVAR** depind de surse web; au fallback dar pot eșua.

## 9. Întrebări pentru consiliu (unde vreau feedback)

**Metodologie (cel mai important):**
1. Grila de teren în 2 etape, selecția pe **ajustarea brută minimă pe etapa de proprietate** (ofertă→tranzacție necontorizată) — e corectă și defensabilă în fața unei bănci/ANEVAR?
2. Grila de casă pe **preț total** cu diferența de arie utilă ca ajustare valorică — corectă, sau ar trebui altă tratare (ex. preț unitar)?
3. Reconcilierea + alocarea (construcții = proprietate − teren) — adecvată pentru garantare?
4. Abordarea prin venit (capitalizare directă + DCF) și grila de chirii — corecte ca structură?
5. Lipsește vreo abordare/verificare cerută de SEV/GEV pentru scopul de garantare?

**Conformitate & risc:**
6. Modelul GDPR (anonimizare înainte de AI) — suficient pentru un instrument profesional? Riscuri reziduale?
7. Modulul AML — abordarea „propune, evaluatorul transmite" e corectă legal? Ce ar trebui neapărat validat juridic?
8. Răspunderea profesională: e periculos ca un AI să redacteze textul de analiză, chiar revizuit de evaluator?

**Arhitectură & inginerie:**
9. Alegerea server-rendered + `.exe` offline (vs. web app) — potrivită pentru acest public/uz? Compromisuri ratate?
10. Riscuri de scalare/mentenanță în arhitectura actuală (FastAPI + Jinja + SQLite local)?
11. Scraping-ul de portaluri ca sursă primară de comparabile — risc legal/tehnic; alternative?

**Produs & distribuție:**
12. Pentru un evaluator real: ce ar face acest raport **respins** de o bancă? Ce lipsește ca să fie „gata de producție"?
13. Distribuția (`.exe` nesemnat, Win10+) — ce probleme practice de adopție vedeți?
14. Care 3 lucruri ar trebui prioritizate înainte de uz real?

---

*Notă pentru reviewer: răspunsurile care indică „așa nu se face" sunt cele mai utile.
Domeniul e reglementat (ANEVAR/SEV 2025, Legea 129/2019) — corectitudinea de standard
și de conformitate primează asupra eleganței tehnice.*
