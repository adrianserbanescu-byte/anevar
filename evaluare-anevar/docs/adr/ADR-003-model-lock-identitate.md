# ADR-003: Modelul de identitate al dosarului + lock-ul la asumare

**Status:** Acceptat (2026-06-07) — **declanșator DECIS de Adi (`BLOCAT-pe-Adi.md` #10): HIBRID TRIPLU** =
(1) checkpoint de asumare (om-în-buclă) + (2) prima generare `.docx` + (3) **upload fișier submis**
(ex. raport editat returnat de bancă/client). **Fundația e implementată** (amprentă de integritate per
versiune + `asumat_la` + trigger upload-submis); rămâne de construit enforcement-ul read-only + clonarea +
de-lock + `.lock` (vezi Action Items).
**Date:** 2026-06-06 (revizuit 2026-06-07 cu decizia #10)
**Deciders:** proprietarul proiectului (Adrian)

## Context

Un dosar de evaluare trebuie să aibă o **identitate stabilă**: ce proprietate, pentru ce scop, al
cui. Această identitate are trei roluri care converg:

1. **Integritate metodologică / audit (SEV 2025, GEV 520):** un raport asumat trebuie să fie
   **inalterabil** — odată ce evaluatorul își pune semnătura, datele care l-au produs nu se mai
   pot schimba „pe tăcute".
2. **Anti-abuz comercial (vezi `4-comercializare.md`):** creditul AI se leagă de **identitatea
   proprietății**. Fără un lock, abuzul evident e „plătesc 1 raport, schimb adresa, scot 50".
3. **UX:** rigiditatea e acceptabilă **doar** dacă schimbarea identității **clonează munca tehnică**
   (comparabile, calcule) — altfel userii caută workaround-uri.

Starea actuală a codului (`dosare_fs.py`): `CAMPURI_IDENTITATE` = `(scop, tip_proprietate,
nume_client, id_client, judet, localitate)`, recalculată la fiecare `salveaza_wizard`. Nimic nu e
încă blocat; `nume_client` e free-text și instabil („Ion Popescu" vs. „Popescu Ion").

Decizii deja luate de council + plan-UI:

- **Council Q1 (consens puternic, Sonnet #1):** identitatea „tare" = `(scop, tip_proprietate,
  COD FISCAL client [CNP/CUI], județ, localitate)`. **Exclude `nume_client`** din identitatea tare
  (ancora stabilă e codul fiscal; numele rămâne editabil). Lock automat la **prima generare reușită
  de `.docx`** (nu la draft/calcul). Schimbarea unui câmp tare → dialog „DOSAR NOU; clonez datele
  tehnice?". Corecturi tipografice → buton „Deblochează corectură", înregistrat în **Audit**.
  (`9-topicuri-decizie.md` Topic 1)
- **Council pe plan-UI (consens 4 modele):** lock la checkpoint-ul de asumare → ireversibil +
  timestamp + **hash SHA256 al folderului** (audit inalterabil) + de-lock cu motiv + audit trail;
  fișier **`.lock`** pentru deschidere concurentă → read-only. (`council-plan-UI-nou.md` §1.3, §3)

## Decision

### 1. Setul de identitate „tare"
Identitatea blocabilă a dosarului = **`(scop, tip_proprietate, cod_fiscal_client [CNP/CUI], județ,
localitate)`**. `nume_client` **iese** din identitatea tare (rămâne editabil; ancora e codul fiscal).
`CAMPURI_IDENTITATE` din `dosare_fs.py` se aliniază: `id_client` devine explicit cod fiscal, nu
free-text generic.

### 2. Lock la asumare — **trigger HIBRID TRIPLU (decizia Adi #10)**
Identitatea se asumă (și apoi trece read-only) la **oricare** din trei momente:
1. **Checkpoint de asumare** — bifa „îmi asum" care deblochează «Generează» (om-în-buclă, deja existent).
2. **Prima generare reușită de `.docx`** (`tip="generat"`).
3. **Upload fișier submis** (`tip="submis"`) — raportul finalizat returnat de bancă/client, încărcat în dosar.

**Implementat (2026-06-07):** fiecare versiune `.docx` salvată (`generat`/`submis`/`import`) primește o
**amprentă SHA256** + moment în `dosar.json` (`versiuni[]`); prima versiune `generat`/`submis` setează
`asumat_la`. `verifica_integritate(uid)` reverifică hash-ul fiecărei versiuni → **tamper-evidence** (apare în
urma de audit). Endpoint: `POST /api/dosar/{uid}/incarca-submis`. *(Hash-ul e per fișier `.docx` asumat — mai
robust decât hash de folder, fiindcă folderul se schimbă la fiecare auto-save; detectează alterarea
fișierului asumat.)*

### 3. Schimbarea identității = dosar nou (clonare)
Editarea unui câmp tare pe un dosar blocat → dialog roșu „Modifici identitatea = **DOSAR NOU**;
clonez datele tehnice + comparabilele?". Confirmarea creează un `uuid` nou cu munca tehnică
copiată; dosarul original rămâne intact (și, comercial, consumă **1 credit** nou).

### 4. De-lock controlat (corectură tipografică)
Buton „Deblochează corectură tipografică" → cere **motiv**, scrie o intrare în **Audit** (cine,
când, de ce). Pentru greșeli de tastare, fără a deschide poarta către modificarea liberă a unui
raport asumat.

### 5. `.lock` pentru concurență
La deschiderea unui dosar se creează un fișier **`.lock`** în folder. Dacă dosarul e deja deschis
(alt proces/instanță), a doua deschidere intră **read-only** — anti-coruptie pe storage-ul pe
foldere (relevant și pentru editări manuale în Explorer).

## Options Considered

### Identitate: include vs. exclude `nume_client`
**Inclus (azi):** numele intră în identitate.
**Cons:** instabil ortografic („Ion Popescu"/„Popescu Ion"/diacritice) → false „identități noi"
sau dosare imposibil de regăsit. **Exclus (decis):** codul fiscal (CNP/CUI) e ancora unică și
stabilă; numele rămâne afișat/editabil. → **Exclus din identitatea tare.**

### Declanșatorul de lock: la calcul vs. la prima generare `.docx` vs. la checkpoint de asumare explicit
| Declanșator | Pro | Contra |
|-------------|-----|--------|
| La **calcul** | blochează devreme | ucide iterația de calibrare; userul nu a „asumat" încă nimic |
| La **prima generare `.docx`** (council Q1) | aliniat cu „a produs un livrabil"; permite iterații | „generare" ≠ neapărat „asumare" dacă userul doar previzualizează |
| La **checkpoint de asumare explicit** (bifă) (plan-UI) | intenție clară a evaluatorului | un pas în plus; trebuie definit unde stă bifa |

→ **Decizie deschisă (Adi, `BLOCAT-pe-Adi.md` #10):** „prima generare `.docx`" și „checkpoint de
asumare bifat" sunt apropiate dar **nu identice**. Council Q1 spune prima generare; planul-UI spune
checkpoint de asumare. Recomandarea convergentă: lock la **prima generare `.docx` asumată**
(generarea cere bifa de asumare — vezi Topic 7), dar **alegerea finală a momentului e a lui Adi**.

### Audit: timestamp simplu vs. hash SHA256 al folderului
**Doar timestamp:** ieftin, dar nu dovedește că **conținutul** nu s-a schimbat.
**Hash SHA256 al folderului (decis):** orice modificare ulterioară a fișierelor devine
**detectabilă** → inalterabilitate verificabilă, aliniată cerinței de audit SEV. Cost: recalcul la
asumare (neglijabil pentru un dosar). → **Hash SHA256.**

### Concurență: fără protecție vs. `.lock`
Fără protecție, două instanțe care scriu `dosar.json` simultan se pot corupe reciproc (storage pe
foldere, scrieri din mai multe surse, inclusiv Explorer). **`.lock` + read-only la a doua
deschidere** e mecanismul minim și standard. → **`.lock`.**

## Consequences

### Pozitive
- **Audit inalterabil** (hash SHA256) aliniat SEV 2025 / GEV 520 — argument de conformitate puternic.
- **Anti-abuz comercial** „din construcție": creditul legat de identitate, schimbarea → dosar nou.
- **Identitate stabilă** (cod fiscal) → regăsire fiabilă, fără false-pozitive ortografice.
- **Concurență sigură** pe storage-ul pe foldere (`.lock`).
- Rigiditate **acceptabilă UX** datorită clonării muncii tehnice.

### Negative
- **Cost cognitiv:** dialogul „dosar nou" poate surprinde; mitigat prin clonare + text clar.
- **Risc de inconsistență dacă userul schimbă clientul după generare** → mitigat de dialogul roșu
  obligatoriu (council Q1).
- **De-lock-ul e o suprafață sensibilă:** dacă e prea permisiv, subminează inalterabilitatea →
  strict pe „corectură tipografică" + motiv obligatoriu în Audit.
- **Cuplaj comercial:** definiția identității leagă audit-ul de facturare; o schimbare ulterioară a
  setului de câmpuri atinge ambele.
- Recalcul hash la asumare (neglijabil) + gestiunea fișierelor `.lock` orfane (la crash → curățare
  la pornire).

## Action Items

1. [x] ✅ **Declanșator DECIS (Adi #10):** HIBRID TRIPLU = asumare + prima generare `.docx` + upload submis.
2. [x] ✅ **Implementat:** `asumat_la` + **amprentă SHA256 per versiune** în `dosar.json`; `verifica_integritate` în urma de audit (tamper-evidence). (`dosare_fs.py`, `web/routers/curent.py` audit.txt, `tests/test_dosare_fs.py`)
3. [x] ✅ **Implementat (trigger #3):** `POST /api/dosar/{uid}/incarca-submis` + buton UI „Înregistrează fișierul submis" (tab Generează).
4. [ ] **Enforcement read-only** pe câmpurile de identitate după asumare + dialog „Modifici identitatea = DOSAR NOU" + clonare date tehnice (uuid nou). *(UX — următorul pas, cuplat cu #5)*
5. [ ] Aliniază `CAMPURI_IDENTITATE` (scoate `nume_client` din identitatea tare; `id_client` = cod fiscal CNP/CUI). *(decizie de produs — atinge numele folderelor + dosarele existente)*
6. [ ] Buton „Deblochează corectură tipografică" → motiv + intrare în Audit.
7. [ ] Fișier `.lock` per dosar la deschidere + read-only la deschidere concurentă; curățare `.lock` orfane la pornire.

> **Stare:** declanșatorul e DECIS (#10) și **fundația de audit-inalterabil (hash per versiune + asumat_la +
> trigger upload-submis) e implementată și testată.** Rămâne de construit **enforcement-ul read-only +
> clonarea + setul de identitate cod-fiscal** (decizii de UX/produs — Action Items 4-5) + de-lock + `.lock`.
