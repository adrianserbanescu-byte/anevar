# Output 1 — Investigație „Descoperă" (redesign comparabile)

> Investigație factuală pentru redesign-ul paginii „Descoperă". Verificată pe **cod** + **anunțuri reale**
> (fetch live, 2026-06-07). Scop: să înțelegem ce info cerem azi fiecărui portal, ce ne întoarce, cum
> se potrivește dicționarul nostru cu realitatea, și dacă un API (Perplexity) poate înlocui scraping-ul.
> Rulată de Sesiunea B. Sursa de adevăr = codul; exemplele sunt anunțuri reale din Breaza/Prahova.

## Rezumat executiv (TL;DR)
- **Căutare automată = doar imobiliare.ro + storia.ro** (OLX nu e în căutare — doar prin extensie). Granularitate = **județ + localitate**; categorii **doar casă + teren**.
- **storia** dă date STRUCTURATE bogate (`__NEXT_DATA__`); **imobiliare** mai sărac (text); **OLX** doar preț.
- **Modelul de ranking există doar pentru casă (+teren)**; apartament/industrial/agricol/special — nemodelate.
- **Perplexity NU poate găsi/citi anunțuri** (5 teste, ambele portaluri): nu deschide URL-ul dat, face keyword-search pe slug → gol / irelevant / fabricat. **Scraperul nostru, pe același subiect: 8 comparabile reale.**
- Util de la un API de search: **doar descoperirea de SURSE noi** (a găsit portaluri în plus).
- Geocoding/distanțe RO: **fezabil offline** (OSM/Nominatim) — neimplementat azi.

---

## T1 · Ce cerem fiecărui portal + ce ne întoarce

### Ce CEREM (căutare) — confirmat în `portal_search.py`
- Portaluri în căutarea automată: **imobiliare.ro, storia.ro**. **OLX absent** (apare doar prin coada extensiei de browser / import URL direct).
- Segmente de URL (categorii) doar **casă** și **teren**:
  - `imobiliare/casa`: `vanzare-case-vile/judetul-{j}/{localitate}`
  - `imobiliare/teren`: `vanzare-terenuri/judetul-{j}/{localitate}`
  - `storia/casa`: `ro/rezultate/vanzare/casa/{j}/{localitate}`
  - `storia/teren`: `ro/rezultate/vanzare/teren/{j}/{localitate}`
- Granularitate input = **județ + localitate** (în URL). **Niciun** input de stradă / cartier / număr.
- Fără localitate → caută pe județ. Filtru `prefer` taie anunțurile promovate din alte localități (după slug).

### Ce ne ÎNTOARCE (parsare anunț) — `url_parser.py`
Câmpurile `ParsedListing`: `pret, moneda, suprafata (casă), suprafata_teren, titlu, nr_camere, etaje` + caracteristici.
- **storia**: din `__NEXT_DATA__` (JSON Next.js) — cel mai bogat: an, încălzire, material, tip clădire, stare, nr. camere, etaje.
- **imobiliare**: parsare din text — mai sărac.

### Exemple reale (fetch live, Breaza/Prahova)
**imobiliare (3 anunțuri date de owner):**
| Preț | Casă | Teren | An | Material | Note |
|------|------|-------|----|----|----|
| 138.000 € | 226 mp | 400 mp | 2010 | beton | P+1E+M, 6 camere |
| 137.000 € | 200 mp | 300 mp | 2000 | — | P+3E+M, 5 camere, Gura Beliei |
| 184.800 € | 215 mp | 2055 mp | 1996 | bca | centrală gaz, D+P+1E |

**storia (2 anunțuri):**
| Preț | Casă | Teren | An | Încălzire | Material | Note |
|------|------|-------|----|----|----|----|
| 62.500 € | 80 mp | 80 mp | — | — | — | 4 camere, Dâmbovița |
| 112.500 € | 220 mp | 700 mp | 2010 | centrală gaz | lemn | casă individuală, stare bună, 5 camere |

---

## T2 · Dicționarul nostru vs. realitatea

- „Dicționarul importat" = maparea **enum-urilor storia** (`gas/urban/detached/ready_to_use/wood/brick…`) → normalizat RO (`_HEATING/_MATERIAL/_TIP_CLADIRE/_FLOORS/_STARE`). **Tunat pe schema storia.**
- **Extragem MAI MULT decât scorăm:** `material, tip_cladire, nr_camere, etaje` se extrag dar **NU intră în ranking** (formula folosește doar 6 atribute).
- **Goluri:**
  - `finisaj` **nu există** în datele structurate → vine **doar din LLM**.
  - `stare` structural = **text cu 3 valori** (`ready_to_use/to_completion/to_renovation`), dar scoringul vrea **1–5** → potrivirea o face **doar LLM-ul**.
  - Consecință: **două criterii cu pondere mare (stare ×4, finisaj ×3) depind 100% de LLM pe text** — risc de fiabilitate.
- Dicționarul e **casă-centric**: zero atribute pentru apartament/industrial/agricol/special.

### Rankingul actual (din `scoring.py`)
| Atribut | Pondere | Distanță d∈[0,1] | Sursă |
|---|---|---|---|
| Suprafață construită | ×5 | `min(\|s−c\|/s, 1)` | parser |
| An | ×5 | `min(\|s−c\|/25, 1)` | parser |
| Stare (1–5) | ×4 | `min(\|s−c\|/4, 1)` | **LLM** |
| Finisaj (1–4) | ×3 | `min(\|s−c\|/3, 1)` | **LLM** |
| Încălzire | ×2 | 0 / 0.5 / 1 | parser |
| Teren (mp) | ×1 | `min(\|s−c\|/s, 1)` | parser |

`Relevanță = 100 × (1 − Σ(pondere×d) / Σ ponderi cunoscute)`. Nementionate se exclud din numitor; ≥3 lipsă → „încredere scăzută". Reguli speciale: teren = doar suprafață; lipsă suprafață → −30 + „completează manual".

---

## T3 · Eșantion real + precizia locației
- Anunțuri reale parsate corect (vezi T1).
- **Problemă de precizie:** căutarea „Breaza" a întors anunțuri din **Gura Beliei / Nistorești / Valea Tarsei** (vecinătăți scăpate de filtrul pe slug). Granularitate insuficientă → temă centrală a redesign-ului.

---

## T4 · Alte portaluri RO
- **VDI.ro** și **Imoradar24.ro** acoperă **comercial + industrial** — exact golul nostru pe #3/#5.
- Plus: HomeZZ.ro, CompariImobiliare.ro (agregator), Publi24.ro, anuntul.ro.
- **Descoperite de Perplexity (search):** `phimob.ro`, `romimo.ro`, `mervani.ro`, `imopedia.ro`, și un portal **hyperlocal**: `imobiliarebreaza.ro` (agențiile locale listează exact zona).
- Fiecare cere **parser propriu** → modelarea #3/#5 depinde și de adăugarea acestor surse.

---

## T5 · Tooling
- Scraping: folosim deja `fetch_html`-ul nostru — merge live pe ambele portaluri.
- Alte site-uri → parser per-site.
- Geocoding → Nominatim/OSM offline.
- **Perplexity = NEPOTRIVIT pentru citit/găsit anunțuri** (vezi „Dimensiunea API").

---

## T6 · Geocoding / distanțe RO (fezabil, gratuit, offline) — NEIMPLEMENTAT azi
- **Localități → coordonate:** extract OSM România (Geofabrik) / dataset comunitar OSM-RO (CSV/GeoJSON) / SIRUTA → distanță haversine, offline.
- **Stradă → coordonate (offline):** Nominatim/Photon/Pelias pe extract OSM-RO.
- Concluzie: **clar fezabil**; întrebarea reală e *cum îl folosim/ponderăm*, nu *dacă se poate*. (Evaluare de fezabilitate, nu constatare pe cod existent.)

---

## 🔑 Dimensiunea API — Perplexity vs. scraping (5 teste)

Pipeline-ul nostru = **scraping HTTP direct** (`fetch_html`) + parsare HTML/`__NEXT_DATA__` + **LLM (Claude)** pe textul scrapuit. Perplexity NU e în pipeline. Testat riguros:

| Test | Input | Rezultat Perplexity |
|------|-------|---------------------|
| A | extrage din 1 URL storia | `{}` (gol) |
| A+ | extrage din 2 URL-uri storia | **„nu pot accesa"** + citări irelevante (keyword-match pe slug „ATV/vacanță") |
| B | „dă 4 anunțuri cu URL" (forțat) | **fabrică** — 3/4 URL-uri = 404 |
| C | „dă 6 cu preț/supr/an" | refuză onest („văd doar rezumate agregate") |
| D | **găsește comparabile pt subiect (format app), „caută pe tot"** | refuză (vede doar landing-pages) |

**Insight cheie:** Perplexity **nu deschide niciodată URL-ul pe care i-l dai** — face o căutare nouă pe cuvinte din slug. Inaccesibilitatea e **portal-agnostică** (imobiliare ȘI storia).

### Head-to-head (același subiect: casă Breaza ~210 mp, teren 400 mp, an 2005, centrală gaz)
| | Comparabile găsite | URL-uri reale |
|---|---|---|
| **Scraperul nostru** (storia) | **8**, rankate (80/65/65/58/51/48%…) | **4/4 = 200 OK** |
| **Perplexity** | **0** (refuză) | — |

**Concluzie:** pentru **găsirea + citirea comparabilelor**, scraping-ul nostru funcționează deja end-to-end; un API de search **NU îl poate înlocui**. Singurul rol util al unui API de search = **descoperirea de SURSE noi**. Un LLM e sigur la **extracția din textul pe care i-l dăm noi**, nu la regăsirea/citirea anunțurilor.

---

## 💥 Cum reformulează asta brief-ul de council
1. „Criterii per categorie" trebuie precedat de **acoperirea căutării**: azi construim URL doar pentru casă/teren (storia ARE `/vanzare/apartament`, dar nu-l generăm).
2. „Dicționarul" e legat de **storia ca sursă structurată** — orice atribut/categorie nouă depinde de ce expune storia.
3. Distanța: întrebarea nu mai e „se poate?", ci **„cu ce pondere, per tip?"** (fezabil offline).
4. **API/Perplexity:** util doar pentru descoperire de surse, nu pentru extracție — deci „consiliul de API-uri" și-ar avea sensul doar la stratul de descoperire surse.
5. OLX: de decis dacă merită băgat în căutarea automată sau rămâne pe extensie.

> Detaliile integrate + întrebările Q1–Q8 pentru council sunt în `council-brief.md` (același folder).
