# ADR-004: Narativul AI printr-un gateway online propriu

**Status:** Propus — necesită confirmarea Adi (conturi externe + validare juridică transfer LLM — `BLOCAT-pe-Adi.md` #3, #7)
**Date:** 2026-06-06
**Deciders:** proprietarul proiectului (Adrian)

## Context

Aplicația e un **tool desktop offline** vândut evaluatorilor individuali ANEVAR. Singura
componentă care **costă bani la utilizare** și care are sens să fie metrată este **apelul LLM**
pentru narativul textual al raportului. Tot restul (calcul, grile, AML, GDPR, asamblare `.docx`,
narativ-șablon) e local și gratis.

Forțe în joc:

- **Licențiere / anti-piraterie:** dacă cheia LLM e în `.exe`, oricine copiază executabilul are AI
  gratis pe cheia furnizorului. E nevoie de un **punct de control online** care leagă apelul de un
  cont plătit.
- **Metrare = busola „metrezi doar ce te costă":** unitatea facturată = **1 narativ AI per dosar**
  (nu fișierul `.docx`). Re-descărcări, recalcule, editări, AML, GDPR, audit, raport-șablon =
  gratis, nelimitat (`4-comercializare.md`).
- **Costuri reale neglijabile:** ~$0.005/apel; un raport bogat ≈ $0.08–0.10; COGS ~$2–3/lună per
  evaluator activ. **Implicație: cota nu acoperă cost (e ~zero) — e pentru tiering + anti-abuz.**
- **GDPR — punct sensibil (`docs/legal/00-evaluare-juridica-RO.md` §2.4):** spec-ul zice
  „anonimizat", dar pentru că demascarea se face **local** (există hartă de corespondență),
  juridic e **pseudonimizare**, nu anonimizare ireversibilă (Considerentul 26 GDPR). Plus: adresa
  exactă a unui imobil poate fi **indirect identificantă**. Deci textul trimis la AI rămâne **în
  sfera GDPR** → DPA art. 28 + (potențial) transfer extra-UE.
- **Offline-first nenegociabil:** fără internet, aplicația trebuie să producă un raport complet
  (fără lustruirea AI). Dependența online e admisă **doar** pentru felia AI.

## Decision

Narativul AI trece printr-un **gateway online propriu** (Supabase Edge Function + Postgres). App-ul
desktop rămâne **offline pentru tot restul**.

### Ce face gateway-ul (la „Generează AI")
1. **Autentifică** contul (Google Sign-In; magic-link email ca fallback).
2. **Validează sesiunea** (max 2 concurente/cont; a 3-a invalidează cea mai veche).
3. **Verifică cota** (per identitate de proprietate — vezi ADR-003; același dosar regenerat = gratis).
4. **Cheamă LLM-ul cu cheia furnizorului** (cheia stă **în gateway**, niciodată în `.exe`).
5. **Metrează**: scade 1 raport (apel cu `capitol="__raport__"`, **o singură dată/raport**; cele
   6–7 secțiuni narative folosesc numele lor real → nu scad cota) + log de facturare.

### Ce primește gateway-ul (date)
**Doar text pseudonimizat**: identificatorii direcți sunt înlocuiți local cu marcaje
(`[CLIENT]`, `[ADRESA]`, `[CF]`, `[CADASTRAL]`), iar **demascarea se face local**. Tot clientul
(date personale, KYC/AML, fotografii, CF/cadastru) **rămâne pe calculatorul evaluatorului**.

### Roluri GDPR (de confirmat de jurist)
- Pentru **textul narativ**, furnizorul = **persoană împuternicită** (art. 28) → **DPA** necesar;
  pseudonimizarea **atenuează, dar nu elimină** calificarea.
- Pentru **cont/abonament/sesiuni/loguri** (email, identitate Google, IP/oră), furnizorul =
  **operator**.

## Options Considered

### Opțiunea A: Cheie LLM locală în `.exe`
| Dimensiune | Evaluare |
|------------|----------|
| Licențiere | **Inexistentă** (cheia se extrage din binar) |
| Metrare | Imposibilă (niciun punct central) |
| Cost infra | Zero |

**Pros:** zero infrastructură; funcționează 100% offline.
**Cons:** **„teatru de securitate"** — cheia într-un `.exe` distribuit se extrage trivial; abuzul
de cheie cade pe furnizor; nicio cale de a factura sau de a opri partajarea. Eliminat.

### Opțiunea B: Fără AI (doar narativ-șablon)
| Dimensiune | Evaluare |
|------------|----------|
| Cost infra | Zero |
| GDPR | Cel mai simplu (nimic nu pleacă) |
| Propunere de valoare | Slăbită (lipsește diferențiatorul AI) |

**Pros:** offline pur; fără transfer de date, fără DPA, fără dependență online.
**Cons:** pierde diferențiatorul comercial (lustruirea AI a narativului = argumentul „economisești
3h/raport"). Rămâne **fallback-ul** când nu există net/abonament, dar nu poate fi singura ofertă.

### Opțiunea C: Gateway online propriu (recomandat)
Felia AI prin gateway; restul offline; gateway-ul ține cheia, metrează, licențiază.

| Dimensiune | Evaluare |
|------------|----------|
| Licențiere | Reală (apelul cere cont activ + sesiune validă) |
| Metrare/facturare | Centralizată, per raport |
| COGS | ~0 (cota = tiering/anti-abuz, nu acoperire de cost) |
| Dependență online | **Doar** pentru AI (restul rămâne offline) |
| GDPR | Gestionabil (pseudonimizare + DPA + SCC), dar **cu obligații** |

**Pros:** singura opțiune care permite licențiere reală + facturare; cheia nu părăsește serverul;
COGS neglijabil → poți fi generos cu cota; restul aplicației rămâne offline.
**Cons:** introduce **infrastructură online** (Supabase/Stripe/Google) + dependență de net pentru
AI; **obligații GDPR** reale (DPA, transfer extra-UE); cont obligatoriu pentru felia AI.

## Consequences

### Pozitive
- **Licențiere reală** (1 licență = 1 utilizator; 2 sesiuni; a 3-a invalidează) fără a expune cheia.
- **COGS ~0** → cota e instrument de tiering/anti-abuz, nu de acoperire de cost; marjă ~80–95%.
- **Offline-first păstrat:** dependența online există **doar** pentru narativul AI; restul (calcul,
  AML, GDPR, `.docx`, șablon) merge fără net.
- **Suprafață GDPR redusă** prin pseudonimizare locală + demascare locală (argument de vânzare).
- **Cache**: narativul se reține în dosar → regenerare `.docx` după modificări minore = gratis.

### Negative
- **Dependență online pentru AI** + **infrastructură de întreținut** (Supabase edge function,
  Postgres, Stripe, OAuth) — contrar simplității „pur offline".
- **Obligații GDPR reale (RISC — council/legal):**
  - Textul e **pseudonimizat, nu anonim** → rămâne dată personală → **DPA art. 28** obligatoriu.
  - **Transfer LLM extra-UE** (ex. Perplexity/Anthropic în SUA) → necesită temei (SCC) + evaluare
    de transfer; **de validat cu juristul GDPR** (`BLOCAT-pe-Adi.md` #3). Risc de re-identificare
    prin adresă/suprafață/localitate combinate → de întărit mascarea sau de documentat risc rezidual.
  - Încadrare **AI Act** + acoperirea asigurătorului de răspundere pentru rapoarte asistate AI
    (poate exclude → „comercial mort", `BLOCAT-pe-Adi.md` #4).
- **Cont obligatoriu** pentru felia AI (prag de adopție; mitigat de fallback-ul șablon offline).
- **Dependență de furnizorul LLM** (preț/disponibilitate); izolată în gateway → schimbarea
  providerului nu atinge `.exe`-ul.

## Action Items

1. [ ] **Validare juridică (BLOCANT):** jurist GDPR pe DPA art. 28 + **transfer LLM extra-UE/SCC** + încadrare AI Act (`BLOCAT-pe-Adi.md` #3); confirmare asigurător de răspundere (#4).
2. [ ] **Conturi externe (Adi):** Supabase + Google OAuth + Stripe (Faza 0 comercializare, `BLOCAT-pe-Adi.md` #7).
3. [ ] Cheia LLM **doar** ca secret în gateway (niciodată în `.exe`).
4. [ ] Întărește pseudonimizarea (nu doar nume/adresă: și suprafață + localitate + indicii unice combinate) **sau** documentează risc rezidual scăzut.
5. [ ] Metrare **o singură dată/raport** (`capitol="__raport__"`); secțiunile narative nu scad cota.
6. [x] ✅ **Verificat (test):** fără client AI (offline/fără abonament), raportul iese **complet** cu text-șablon (`tests/test_report_generator.py::test_raport_offline_fara_ai_e_complet`). Offline-first confirmat.

> **Decizie cerută Adi:** confirm arhitectura gateway (felia AI online, restul offline) **și**
> declanșez validarea juridică pe transferul extra-UE + deschiderea conturilor externe. Fără
> avizul GDPR + acoperirea asigurătorului, gateway-ul **nu** se lansează comercial.
