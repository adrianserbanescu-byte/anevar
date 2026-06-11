# Crawl anevar.ro — resurse RATATE pentru app evaluare casă+teren (garantare credit)

> **Temă:** `crawl-anevar-ro`. Explorare anevar.ro (+ subdomenii `site2.anevar.ro`, `big.anevar.ro`) pentru
> a identifica **documente / ghiduri / standarde / date oficiale** UTILE aplicației, pe care folderul
> existent NU le conține. Comparat cu inventarul deja analizat în `docs/analiza-anevar/*` și `docs/SEV-2025-*`,
> `docs/GEV520-2025-crosscheck.md`, `docs/conformitate/*`.
>
> **Metodă:** WebFetch e blocat de anevar.ro (403 Forbidden pe TOATE paginile, inclusiv `site2`). Crawl
> efectuat prin WebSearch (descoperă URL-uri reale de PDF din directoarele `/images/_upload/` și
> `/images/documente/`, plus paginile `/p/...`). **NU am descărcat nimic** — doar identificat + rezumat.
>
> ⚠️ Document de inventar/recomandare. Decizia de relevanță și conformitate revine evaluatorului ANEVAR.
> Prioritate: SEV 2025 primează; în rest, documentul mai nou câștigă.

---

## 0. Ce are DEJA userul (ca să nu redescărcăm)

Confirmat în folder / analize existente:
- **SEV 2025** (PDF consolidat `sev-2025.pdf`, ediția în vigoare 1 iul 2025, HCD/Hot. Conf. 2/2025) — include
  TOATE GEV-urile (500, 520, 630, 450 etc.) într-un singur document. Crosscheck-uri făcute: GEV 520, 630, 500, 450.
- **AML:** HCD 58/2023, HCD 62/2025 (analiză), Legea 129/2019 (stub + constante codate), Norme ONPCSB 37/2021
  (stub), formular KYC model, decizie desemnare, norme interne, info RBR/ONRC.
- **Glosar ANEVAR** (citit vizual, `glosar.pdf`).
- **Procedurale:** Procedura de arhivare a dosarelor, Asigurarea calității (recomandări QC), Anexa HCD 74/2022
  (studii de piață art. 111), HCD 55/2017 (bunuri culturale — irelevant), pagina BIG/BIF (impozitare).
- **Articole piață:** 4+4 articole metodologice Adrian Nicolescu (analiza pieței, terenuri, factori de valoare).

**Concluzie inventar:** acoperirea pe **standarde normative** e bună (SEV 2025 e complet). Gap-urile reale
sunt pe: (a) **datele oficiale de piață** (indici, rapoarte rezidențiale trimestriale), (b) **manualul +
fluxul operațional BIG** (garantare credit — exact scopul app-ului), (c) **versiunile ACTUALIZATE** ale
documentelor AML (HCD 62 actualizat oct. 2025), (d) **puncte de vedere ANEVAR** tematice (risc fizic la
garantare, verificarea evaluării), (e) **politica de protecție a datelor ANEVAR** (înlocuită oct. 2025).

---

## 1. RESURSE RATATE — listă cu URL + de ce + prioritate

Legendă prioritate: **🔴 blocant** (lipsă cu impact direct pe conformitate/scop) · **🟠 important**
(întărește conformitatea sau motorul) · **🟡 minor/opțional** (nice-to-have, referință).

### A. Date oficiale de piață (cel mai mare gap — exact inputul motorului)

| # | Resursă | URL | De ce e utilă | Prioritate |
|---|---|---|---|---|
| 1 | **Indicele imobiliar ANEVAR** (pagină) | `https://www.anevar.ro/p/informatii-din-piata/informatii-statistice-anevar/indicele-imobiliar-anevar` | Indicele oficial rezidențial ANEVAR. App-ul are deja `indice_anevar.py` — aceasta e **sursa-ancoră autoritară** pentru a-l valida/actualiza și pentru indexarea comparabilelor în timp (SEV 104 ierarhia datelor). | 🟠 important |
| 2 | **Proprietăți imobiliare / Date din piață** (pagină) | `https://www.anevar.ro/p/informatii-din-piata/date-din-piata/proprietati-imobiliare` | Feed-ul oficial de date de piață rezidențiale (parteneriat analizeimobiliare.ro / imobiliare.ro). Context de piață + sanity-check pentru valorile estimate. | 🟠 important |
| 3 | **Analize imobiliare — rapoarte trimestriale rezidențiale** (PDF-uri) | `https://www.anevar.ro/p/informatii-din-piata/analize-imobiliare` (ex: `.../images/_upload/raport-t2-2021.pdf`, `.../documente/analizeimobiliare_raport_t4_2017.pdf`) | Rapoarte trimestriale „Piața imobiliară rezidențială" — **exact segmentul casă+teren**. Sursă de tendințe de preț pe orașe, util la justificarea ajustărilor și la secțiunea „analiza pieței" din raport (cerută de GEV 630/SEV 105). | 🟠 important |

### B. Flux operațional BIG — garantarea creditului (scopul #1 al app-ului)

| # | Resursă | URL | De ce e utilă | Prioritate |
|---|---|---|---|---|
| 4 | **BIG — Manual de utilizare** (PDF) | `https://www.anevar.ro/images/documente/manual_utilizare_ad-3_0.pdf` | Manualul aplicației BIG (Baza Imobiliară de Garanții): cum se introduc datele raportului, **cum arată recipisa + codul unic**, înregistrări corective. App-ul tratează recipisa BIG doar ca text (gap G-LNP-5 / G5 SEV) — manualul dă structura exactă a câmpurilor BIG de pus în checklist/atașament. | 🔴 blocant (e fix scopul app-ului) |
| 5 | **Baza Imobiliară de Garanții — info** (pagină) | `https://www.anevar.ro/p/informatii-din-piata/big/info` | Descrie ce informații sumare din raport intră în BIG (obligatoriu pentru garantare, GEV 520 §83–84). Definește câmpurile pe care raportul trebuie să le poată exporta către BIG. | 🟠 important |
| 6 | **BIG — Ajutor / Proprietăți evaluate** (pagină) | `https://big.anevar.ro/Home/Ajutor` | Ghidul operațional al portalului BIG live. Util pentru a alinia datele generate de app la formatul de import BIG. | 🟡 minor |

### C. AML — versiuni ACTUALIZATE (userul are analiza, nu PDF-ul actualizat)

| # | Resursă | URL | De ce e utilă | Prioritate |
|---|---|---|---|---|
| 7 | **HCD 62 actualizat cu CFH 74/2025** (PDF) | `https://www.anevar.ro/images/_upload/hcd-62-actualizata-cfh-74-2025.pdf` | Versiunea **consolidată oct. 2025** a formularului standardizat KYC + evaluarea riscului SB/FT. Sursa primară pentru câmpurile KYC lipsă din UI (gap-urile AML G1–G4: scop AML, RBR, modalitate identificare BR, măsuri de atenuare). | 🟠 important |
| 8 | **Ghiduri și documente utile L.129/2019** (pagină-index) | `https://www.anevar.ro/p/profesie/aplicarea-legii-1292019/ghiduri-si-documente-utile-in-aplicarea-legii-1292019` | Pagina-index ANEVAR care listează TOATE modelele AML curente (formular, decizie, norme, ghid risc) + linkuri de download. Verifică dacă vreun model a fost revizuit față de copiile din folder. | 🟠 important |
| 9 | **Obligațiile din Legea 129/2019 pentru evaluatori** (PDF) | `https://www.anevar.ro/images/documente/obligatii_spalarea_banilor_legea_129_2019_1.pdf` | Sinteza ANEVAR a obligațiilor AML pe rolul de entitate raportoare — checklist de conformitate AML, util pt. confirmarea regulilor codate. | 🟡 minor |

### D. Puncte de vedere / poziții oficiale ANEVAR (tematice, direct pe scopul app-ului)

| # | Resursă | URL | De ce e utilă | Prioritate |
|---|---|---|---|---|
| 10 | **PdV ANEVAR — „aprecierea riscurilor fizice" la garantarea împrumutului** | `https://www.anevar.ro/noutate/235/...aprecierea-riscurilor-fizice...` | Poziția oficială pe **riscurile fizice** (climatice/structurale) în evaluarea pentru garantare — leagă direct de gap-ul ESG / „riscul evaluării" (G1 / G-T4, marcat blocant). Spune CE risc fizic trebuie tratat în raport. | 🔴 blocant (acoperă gap ESG existent) |
| 11 | **PdV ANEVAR — verificarea evaluării** (PDF) | `https://www.anevar.ro/images/documente/pdv_ref_verificarea_evaluarii.pdf` | Punct de vedere oficial pe SEV 400 (verificarea evaluării) — alimentează gap-ul G-Q1 (pas de verificare internă a calității pre-emitere). | 🟡 minor |
| 12 | **Poziția oficială a Asociației** (pagină) | `https://www.anevar.ro/p/pozitia-oficiala-a-asociatiei` | Index al tuturor pozițiilor/PdV oficiale ANEVAR — de scanat periodic pentru orice clarificare cu impact pe motorul/raportul app-ului. | 🟡 minor |

### E. Conformitate transversală (GDPR + glosar oficial live)

| # | Resursă | URL | De ce e utilă | Prioritate |
|---|---|---|---|---|
| 13 | **Politica de protecție a datelor ANEVAR — înlocuită oct. 2025** (HCD din 22.10.2025) | listată în `https://www.anevar.ro/p/despre-anevar/transparenta-decizionala/hotarari-ale-consiliului-director/2025` | Una din hotărârile oct. 2025 = **înlocuirea politicii de protecție a datelor/confidențialitate**. Relevant pentru draft-urile GDPR ale app-ului (`docs/politica-GDPR-draft.md`, `docs/gdpr/*`) — de aliniat la noul model ANEVAR. URL PDF exact de găsit în lista 2025. | 🟠 important |
| 14 | **Glosar de termeni — pagina oficială (live, © 2026)** | `https://www.anevar.ro/p/glosar-de-termeni` | Versiunea LIVE a glosarului (userul are doar `glosar.pdf` citit vizual). Sursa canonică pentru auditul terminologic UI+raport (gap-urile G-T1/G-T2: „Scop"→„Utilizare desemnată", „comparatie"→„abordarea prin piață", glosar in-app). | 🟡 minor |

### F. Material de fundamentare metodologică (referință, nu obligatoriu)

| # | Resursă | URL | De ce e utilă | Prioritate |
|---|---|---|---|---|
| 15 | **Bazele evaluării 2024 / brosură examen 2025** (PDF) | `https://www.anevar.ro/images/_upload/brosura-bazele-evaluarii-2024.pdf` (și `...-examen-2025.pdf`) | Manualul de fundamente al evaluării (abordări cost/venit/piață, depreciere, CMBU, alocare teren/construcție). Referință pentru a verifica corectitudinea formulelor din `engine/` + vocabular. | 🟡 minor |
| 16 | **Revista „Valoarea, oriunde este ea"** (PDF-uri) | ex. `https://www.anevar.ro/images/documente/valoarea-14-site.pdf` (+ celelalte numere) | Revista profesională ANEVAR — articole metodologice (un număr e dedicat „Verificarea evaluării"). Userul are articole Nicolescu; Valoarea e sursa oficială, mai largă, pentru context piață + bune practici. | 🟡 minor |
| 17 | **Cărți IROVAL** (magazin) — „Evaluarea proprietății imobiliare", „150+ aplicații" | `https://magazin.iroval.ro/` | Manualele de referință ale institutului ANEVAR de cercetare (IROVAL). **Plătite** (nu download liber) — de menționat ca achiziție opțională, nu ca gap de descărcat. | 🟡 opțional (cost) |

---

## 2. Top recomandare de descărcat (ordine)

1. **#4 BIG Manual de utilizare** + **#5 BIG info** — fluxul de garantare credit e SCOPUL app-ului; recipisa
   BIG e cerință GEV 520 §83–84 și e tratată azi doar ca text (gap G-LNP-5/G5).
2. **#10 PdV riscuri fizice la garantare** — acoperă direct gap-ul blocant ESG/„riscul evaluării" (G1/G-T4).
3. **#1/#2/#3 Date de piață (indice + rapoarte rezidențiale)** — input autoritar pentru motorul de comparabile
   și pentru secțiunea „analiza pieței" din raport (GEV 630/SEV 105).
4. **#7 HCD 62 actualizat (KYC)** + **#8 pagina-index AML** — versiunile curente pt. gap-urile AML din UI.
5. **#13 Politica GDPR ANEVAR (oct. 2025)** — de aliniat draft-urile GDPR ale app-ului la noul model.

---

## 3. Note de crawl

- **WebFetch blocat (403) pe tot anevar.ro** — descoperirea s-a făcut exclusiv prin WebSearch; URL-urile de PDF
  sunt din directoarele reale `/images/_upload/` și `/images/documente/`, dar **nu au fost descărcate/validate
  byte-cu-byte**. Câteva pot fi versiuni vechi (ex. `raport-t2-2021.pdf` — de luat cel mai recent trimestru din
  pagina-părinte `/p/informatii-din-piata/analize-imobiliare`).
- **`site2.anevar.ro`** = mirror cu fișiere `.docx` editabile (ex. `gev_520_..._.docx`, `..._sev_400_...pdf`) —
  util dacă se vrea varianta text a unui standard, dar SEV 2025 consolidat (`sev-2025.pdf`) le suprascrie.
- Documente de pe site-uri terțe (scribd, evexpert, eval.ro) = NU sursă oficială; ignorate ca gap.

**Documente conexe (folder):** `docs/analiza-anevar/*`, `docs/SEV-2025-*.md`, `docs/GEV520-2025-crosscheck.md`,
`docs/conformitate/*`, `src/evaluare/indice_anevar.py`, `docs/politica-GDPR-draft.md`.
