# ADR-001: Decompoziția aplicației web în routere pe domenii

**Status:** Accepted — implementat (app.py 460 → 27 linii; 6 routere pe domenii)
**Date:** 2026-06-04
**Deciders:** proprietarul proiectului (Adrian)

## Context

`src/evaluare/web/app.py` are **460 de linii** și definește **29 de rute** ca funcții
imbricate (closures) în interiorul fabricii `create_app(storage, client, fetcher)`.
Rutele captează prin closure dependențele partajate: `storage`, `client` (narator AI),
`fetcher` (HTTP injectabil), plus `templates` și helperul `_doc_response` create local.

Forțe în joc:

- **Lizibilitate/navigare:** un singur fișier amestecă 6 domenii (evaluare, grile,
  descoperire, AML, instrumente piață, pagini HTML). Găsirea unei rute presupune
  scroll printr-un fișier mare.
- **Risc de coliziune:** orice modificare la orice domeniu atinge același fișier.
- **Constrângere de ambalare:** produsul e un singur `.exe` offline (PyInstaller).
  Orice import nou trebuie să rămână în pachetul `evaluare.*` (fără I/O extern la pornire).
- **Injecția prin closure funcționează și e testată:** `create_app` primește
  dependențele și le injectează; testele construiesc app-ul cu `storage` temporar și
  `client=None`. Nu vrem să stricăm acest contract (375 teste verzi).
- **Urgență mică:** auditul de datorie tehnică a evaluat acest item la prioritate **15**
  (cea mai joasă din lot). Nu rezolvă un bug; e igienă structurală.

## Decision

Propunem **Opțiunea C — funcții-fabrică de routere pe domeniu**: fiecare domeniu devine
un modul `web/routers/<domeniu>.py` care expune
`build_<domeniu>_router(deps) -> APIRouter`, iar `create_app` doar compune routerele
(`app.include_router(...)`). Dependențele partajate se grupează într-un mic obiect
`Deps` (dataclass: `storage`, `client`, `fetcher`, `templates`), păstrând **exact**
modelul de injecție actual — fără `Depends()` global, fără stare ascunsă.

Comportamentul rămâne **byte-identic** (aceleași căi, aceleași răspunsuri); refactorul e
strict mecanic și acoperit de suita existentă.

## Options Considered

### Option A: Status quo (un singur fișier)
| Dimensiune | Evaluare |
|------------|----------|
| Complexitate | Mică (nu se schimbă nimic) |
| Cost | Zero |
| Scalabilitate | Slabă — fișierul crește cu fiecare feature |
| Familiaritate | Maximă |

**Pros:** zero risc, zero efort.
**Cons:** fișierul continuă să crească; navigare/coliziuni tot mai dificile.

### Option B: Routere cu `Depends()` + `app.state`
Dependențele se pun pe `app.state` și se injectează în rute prin `Depends(get_storage)`.

| Dimensiune | Evaluare |
|------------|----------|
| Complexitate | Medie-mare |
| Cost | Mediu (rescrii fiecare semnătură de rută) |
| Scalabilitate | Bună |
| Familiaritate | Mai mică (idiom FastAPI nou pentru acest cod) |

**Pros:** idiom „canonic" FastAPI; testabil prin override de dependențe.
**Cons:** schimbă contractul de injecție testat; `client=None`/`fetcher` injectat devin
provideri pe `app.state`; mai multă mașinărie pentru un câștig identic ca Opțiunea C;
risc mai mare de regresie pe 29 de rute.

### Option C: Funcții-fabrică de routere (recomandat)
Fiecare domeniu: `def build_grile_router(d: Deps) -> APIRouter`. `create_app` devine ~30 linii.

| Dimensiune | Evaluare |
|------------|----------|
| Complexitate | Mică-medie |
| Cost | Mic (mutare mecanică, fără rescriere de logică) |
| Scalabilitate | Bună — feature nou = modul nou de router |
| Familiaritate | Mare — păstrează exact closure-injection-ul actual |

**Pros:** păstrează contractul de injecție testat; diff mecanic; fișiere mici pe domeniu;
`create_app` devine un index lizibil; zero schimbare de comportament.
**Cons:** un mic obiect `Deps` în plus; 6-7 fișiere noi în loc de unul.

## Trade-off Analysis

B și C ajung la aceeași destinație (routere pe domenii). Diferența e **cum** injectăm
dependențele. Codul actual **deja** funcționează prin closures pe argumentele lui
`create_app`; Opțiunea C păstrează exact acest model (doar îl mută în funcții-fabrică),
deci diff-ul e mecanic și suita existentă îl validează direct. Opțiunea B înlocuiește
modelul cu `Depends()`/`app.state` — un câștig de „idiomatică" care nu aduce nicio
capabilitate în plus aici, dar adaugă suprafață de regresie pe toate cele 29 de rute.
Pentru un produs offline cu injecție simplă și deja testată, **C oferă tot beneficiul
structural al lui B la o fracțiune din risc**.

Grupare propusă (6 routere + paginile):

| Modul | Rute |
|-------|------|
| `routers/evaluare.py` | `POST/GET /api/evaluare*`, `raport.docx`, `audit.txt`, pagina `/evaluare/{eid}` |
| `routers/grile.py` | `/api/grila-teren\|casa\|chirii`, pagina `/grila` |
| `routers/descoperire.py` | `/api/descopera`, `/api/descopera-teren`, pagina `/descoperire` |
| `routers/aml.py` | cele 7 rute `/api/aml/*`, pagina `/aml` |
| `routers/piata.py` | `/api/curs-bnr`, `/api/indice-anevar`, `/api/localitati`, `/api/zona`, `/api/ingestie`, `/api/import-url` |
| `routers/pagini.py` | `/`, `/formular`, `/wizard` |

## Consequences

- **Mai ușor:** localizarea și modificarea unei rute; adăugarea de domenii noi;
  citirea `create_app` ca index.
- **Mai greu:** o schimbare care atinge `Deps` (semnătura partajată) atinge toate
  routerele — dar asta e rar și explicit.
- **De revizitat:** dacă vreodată mutăm la `Depends()` (Opțiunea B) pentru override
  granular în teste, `Deps` e punctul natural de pornire.
- **Neschimbat:** spec-ul PyInstaller (bundle-ul include pachetul), comportamentul
  rutelor, testele.

## Action Items

1. [ ] Introdu `web/deps.py` cu dataclass-ul `Deps(storage, client, fetcher, templates)`.
2. [ ] Creează `web/routers/` și mută rutele pe domenii (mecanic, fără schimbări de logică).
3. [ ] Mută `_doc_response` în `routers/aml.py`; `_fmt_numar` rămâne util partajat
   (în `routers/evaluare.py` sau un `web/_format.py`).
4. [ ] `create_app` păstrează aceeași semnătură și compune routerele via `include_router`.
5. [ ] Rulează suita (375 teste) — trebuie să rămână verde fără modificări de teste.
6. [ ] Rebuild `.exe` + smoke pe `/wizard`, `/grila`, `/aml`, un `POST` din fiecare router.
7. [ ] Actualizează `README.md` (secțiunea Structura) cu `web/routers/`.

**Decizie cerută:** aprob Opțiunea C? Dacă da, o implementez ca pas separat, strict
aditiv și verificat cu suita + smoke pe exe.
