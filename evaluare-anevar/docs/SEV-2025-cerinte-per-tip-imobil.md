# SEV 2025 — cerințe UNICE per tip de imobil (LIVRABIL 2)

> **Cerința centrală Adi:** „ce e UNIC per tip, ca app-ul să ceară DOAR ce e necesar per tip".
> Acest document este o **matrice**: pentru fiecare tip de imobil din aplicație, ce abordări de valoare se
> aplică (și de ce), ce date de intrare specifice, ce ajustări, ce elemente de raport și ce verificări de
> conformitate sunt **UNICE** față de restul. Scop: UI-ul să afișeze/ceară **doar ce contează** pentru
> tipul ales.
>
> **Tipuri din cod** (`src/evaluare/profil.py`, `TipActiv`): `casa`, `apartament`, `teren`, `comercial`,
> `industrial`, `agricol`, `special`. UI-ul (`web/templates/curent/dosar.html`, dropdown linia 127–130)
> expune azi: **casa, apartament, industrial, agricol, special** (lipsesc `comercial` și `teren` standalone).
>
> **Sursă normativă:** SEV 2025 — GEV 630 (metodologie), SEV 230 (drepturi), GEV 232 (PGA), GEV 520
> (garantare), SEV 233 (în construire). Citatele = numerotarea internă a fiecărui standard.

---

## 0. Sinteza vizuală — ce abordare e PRINCIPALĂ per tip

| Tip | Abordare principală | Secundare/coroborare | Ghid | De ce (standard) |
|---|---|---|---|---|
| **casă + teren** | **piață (comparație)** | cost (construcție + teren) | GEV 630 / GEV 520 | piață lichidă rezidențială; cost util la construcții noi (§73) |
| **apartament** | **piață (comparație)** | — (cost rar; teren = cotă indiviză netranzacționabilă) | GEV 630 / GEV 520 | populație statistică omogenă (GEV 520 §66.2.i); fără teren standalone |
| **teren (liber)** | **piață (comparație vânzări)** | extracție, alocare, reziduală, capit. rentă | GEV 630 §81–102 | comparația = cea mai adecvată la teren (§83) |
| **comercial (închiriat / PGA)** | **venit** | piață (verificare), cost rar | GEV 630 / GEV 232 | proprietate generatoare de venit; PGA → venit (GEV 232 §11) |
| **industrial / hală** | **piață sau cost** (după lichiditate) | venit dacă închiriat | GEV 630 | construcții uneori specializate (§73 cost); evită cost ca principal la garantare (GEV 520 §31) |
| **agricol** | **piață (comparație)** | capit. rentă funciară | GEV 630 | teren agricol = populație omogenă (GEV 520 §66.2.i) |
| **special / specializat** | **cost (CIN)** sau venit | — (lipsă piață) | GEV 630 / SEV 230 §90.3 | fără tranzacții comparabile → cost de înlocuire net (SEV 230 §90.3) |

> **Regulă transversală la garantare (GEV 520 §31):** pentru bunuri imobile, **abordarea prin cost să NU
> fie principală** (lichiditate). Cost devine relevant doar când lipsește piața ȘI nu se poate aplica venit
> (§34) — și atunci cu **accept scris** al creditorului.

---

## 1. COMUN la TOATE tipurile (de cerut mereu)

Indiferent de tip, standardul cere (GEV 630 §11–29, §110–112; SEV 230 §40; GEV 520):

- **Termeni de referință:** identificare evaluator/client/**utilizator desemnat**, proprietate, monedă,
  utilizare desemnată, tip + premisa valorii, **data evaluării / raportului / inspecției**, ipoteze,
  declarația de conformitate.
- **Dreptul evaluat** (SEV 230 §40.1): proprietate deplină / cotă / superficie / uzufruct / servitute.
- **Identificare cadastrală:** adresă, **nr. cadastral**, **carte funciară**, **act de proprietate**,
  **sarcini** (ipoteci/servituți din CF — critic la garantare).
- **Inspecție** (GEV 520 §44 — **interior + exterior obligatoriu** la garantare): data, persoana (evaluator
  autorizat), însoțitorul, neconcordanțe scriptic↔faptic.
- **Suprafețe** din document autorizat (GEV 630 §25); Au ≤ Acd.
- **Analiza pieței / aria de piață** specifică tipului (GEV 630 §30–34).
- **CMBU** — concluzia (GEV 630 §35–39).
- **Reconciliere argumentată**, fără medie aritmetică (§107); regula 20% (§109).
- **Raportare** conform SEV 106 + comentariu de performanță a garanției (GEV 520 A5 a–d).
- **ESG** (GEV 520 §86–88): riscuri fizice + certificat energetic, cu disclaimer de competență.
- **BIG** (GEV 520 §58, §83) — recipisă (excepție ANAF §78).

Restul documentului = **ce se ADAUGĂ / SCHIMBĂ per tip**.

---

## 2. CASĂ + TEREN (`casa`)

| Dimensiune | Specific |
|---|---|
| **Abordări** | **Piață** (principală) + **cost** (CIN construcție + valoare teren). Profil cod: `["cost","comparatie"]`, ghid `GEV_520`. |
| **Date de intrare UNICE** | Componente de cost ale construcției (pentru CIB segregat), an construire, tabel depreciere fizică, **valoarea/grila terenului separat** (terenul se evaluează distinct — GEV 630 §81–102). |
| **Ajustări specifice** | Grilă piață pe elemente: drepturi, finanțare, condiții vânzare, **localizare**, caracteristici fizice (suprafață, finisaje, an), economice (GEV 630 §56). |
| **Elemente de raport UNICE** | **Alocarea valorii** teren/construcție (la garantare **nu e necesară** dacă se ia în întregime — GEV 520 §38); depreciere (fizică/funcțională/externă) cu justificare. |
| **Verificări conformitate** | Min 3 comparabile; depreciere funcțională/externă ≠0 → justificare scrisă; cost ≠ principal (GEV 520 §31). |

## 3. APARTAMENT (`apartament`)

| Dimensiune | Specific |
|---|---|
| **Abordări** | **Piață** (principală). Cost rar aplicabil (terenul = **cotă indiviză netranzacționabilă** → nu se alocă separat — GEV 630 §118.a). Profil cod: `["comparatie","cost"]`. |
| **Date de intrare UNICE** | **etaj**, **nr. niveluri bloc**, **an bloc**, **cotă teren indiviză** (mp). **NU are teren standalone** (UI ascunde `grup-teren` — `dosar.html` §831). |
| **Ajustări specifice** | Etaj/poziție în bloc, vechime bloc, dotări comune; comparabile = alte apartamente similare. |
| **Elemente de raport** | Fără alocare teren/construcție (terenul nu e tranzacționabil separat — GEV 630 §118.a interzice modul a). |
| **Verificări conformitate** | Etaj ≤ nr. niveluri bloc (`validation.py:43`). **Eligibil pentru evaluare globală/AVM** la monitorizare (GEV 520 §66.2.i) — populație statistică omogenă. |

## 4. TEREN liber (`teren`) — *azi nereprezentat ca tip principal în UI*

| Dimensiune | Specific |
|---|---|
| **Abordări** | **Piață — comparația vânzărilor** (cea mai adecvată — GEV 630 §83). Alternative când lipsesc comparabile: **extracție** (§92), **alocare/proporție** (§93), **metoda reziduală** (§97, cere autorizație de construire), **capitalizarea rentei funciare** (§99), **analiza parcelării/dezvoltării** (§101, DCF). |
| **Date de intrare UNICE** | **Certificat de urbanism** (POT, CUT, destinație, restricții — GEV 630 §16, GEV 520 §46), zonare, utilități, acces, **coordonate Stereo 70** (GEV 520 §52). Fără construcție (UI ascunde `grup-constructie`). |
| **Ajustări specifice** | Drepturi, finanțare, condiții, **localizare, caracteristici fizice, acces, utilități, zonare** (GEV 630 §90). Comparabilele = **aceeași CMBU** (§91). |
| **Elemente de raport** | CMBU a terenului ca **liber** (§81); **NU** se aplică metoda comparației prin bonitare (Decizia PMB 79/1992) — explicit nerecunoscută (§86). |
| **Verificări conformitate** | Min 3 comparabile de teren (validatorul `valideaza_comparabile_teren` există). |

## 5. COMERCIAL / generator de venit (`comercial`) — *azi nereprezentat în dropdown UI*

| Dimensiune | Specific |
|---|---|
| **Abordări** | **Venit** (principală — capitalizare directă sau DCF). Piață = verificare. **Cost de regulă NU se aplică** (GEV 232 §11). Profil cod: `COMERCIAL_INCHIRIAT = ["venit","comparatie"]`, ghid `GEV_630`. |
| **Date de intrare UNICE** | **Venit brut potențial**, grad de neocupare, cheltuieli de exploatare (cele ale **proprietarului**, nerecuperabile — GEV 630 §70), **rată de capitalizare/actualizare**; contracte de închiriere; pentru DCF: fluxuri + rată actualizare + valoare reziduală. |
| **Ajustări specifice** | Corelarea **tipului de venit cu tipul de rată** (net↔net, brut↔brut — GEV 630 §64, paragraf NOU 2025). Atenție la **chirie peste piață** (GEV 520 A6 — ignoră sau contabilizează risc). |
| **Elemente de raport UNICE** | NOI (venit net din exploatare), ipoteze de venit argumentate (§71); pentru **PGA** (hotel, benzinărie etc.): scenariu de bază convenit cu creditorul — going concern / **OER** / utilizare alternativă / încetare (GEV 520 A9, GEV 232). |
| **Verificări conformitate** | Venit ≠ din afacere fără a trata componenta de active necorporale (SEV 230 §80.3 → SEV 200/210). **Exclus de la evaluarea globală** (GEV 520 §67.a). |

## 6. INDUSTRIAL / hală (`industrial`)

| Dimensiune | Specific |
|---|---|
| **Abordări** | **Piață sau cost** (după lichiditatea pieței); **venit** dacă e închiriat. Profil cod: `INDUSTRIAL = ["cost","venit","comparatie"]`, ghid `GEV_630`. |
| **Date de intrare UNICE** | **Înălțime liberă** (m) (UI: `ind-fields`), deschideri, portanță, dotări tehnice; pentru cost: componente de construcție specializate. |
| **Ajustări specifice** | Caracteristici tehnice (înălțime, travee), localizare logistică, acces TIR/CF. |
| **Elemente de raport** | La construcții specializate fără piață → cost de înlocuire net (SEV 230 §90.3); depreciere **funcțională** (neadecvare tehnologică) frecvent relevantă (GEV 630 §78.b). |
| **Verificări conformitate** | La garantare, cost ≠ principal fără justificare lipsă piață+venit (GEV 520 §31, §34). **Exclus de la evaluarea globală** (GEV 520 §67.a — hale industriale). |

## 7. AGRICOL (`agricol`)

| Dimensiune | Specific |
|---|---|
| **Abordări** | **Piață (comparație)** (principală). Alternativ: **capitalizarea rentei funciare** (GEV 630 §99). Profil cod: `AGRICOL = ["comparatie"]`, ghid `GEV_630`. |
| **Date de intrare UNICE** | Categorie de folosință, clasă de bonitate/fertilitate, suprafață, acces, irigații; **fără construcție** (UI: `agr-fields`, ascunde `grup-constructie`). |
| **Ajustări specifice** | Productivitate sol (SEV 230 §40.8.d), formă/comasare parcelă, acces, zonă. |
| **Elemente de raport** | CMBU agricolă vs. potențial de schimbare destinație; **atenție** la terenuri inundabile / cu alunecări — excluse de la evaluarea globală (GEV 520 §67.d). |
| **Verificări conformitate** | **Eligibil pentru evaluare globală/AVM** la monitorizare (GEV 520 §66.2.i) — teren agricol = populație omogenă. |

## 8. SPECIAL / specializat (`special`)

| Dimensiune | Specific |
|---|---|
| **Abordări** | **Cost (CIN)** sau **venit** — lipsește piața de comparabile (SEV 230 §90.3: cost ca abordare principală când nu există dovezi de preț/venit). Profil cod: `SPECIAL = ["venit","comparatie","cost"]`, ghid `GEV_630`. |
| **Date de intrare UNICE** | Componente de cost detaliate (devize / costuri segregate — GEV 630 §76); pentru construcții vechi specializate fără cost de reconstruire → **indici de cost** pe cost istoric (§75). |
| **Ajustări specifice** | Depreciere fizică + **funcțională** + **externă/economică** (toate trei frecvent relevante — §78). |
| **Elemente de raport** | Justificarea alegerii cost de înlocuire vs. reconstruire (§74–75); echivalent modern (SEV 230 §90.5). |
| **Verificări conformitate** | Depreciere funcțională/externă ≠0 → justificare scrisă (`validation.py:130`). **Exclus de la evaluarea globală** (GEV 520 §67.a — construcții speciale). |

---

## 9. Matrice de DATE DE INTRARE per tip (ce câmpuri să ceară UI-ul)

Legendă: ● obligatoriu · ○ opțional/condiționat · — nu se aplică

| Câmp / Tip | casă | apart. | teren | comercial | industrial | agricol | special |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| Grilă piață (comparabile clădire) | ● | ● | — | ○ | ● | — | ○ |
| Grilă teren | ● | — | ● | ○ | ● | ● | ○ |
| Componente cost construcție | ● | ○ | — | — | ● | — | ● |
| Tabel depreciere | ● | ○ | — | — | ● | — | ● |
| etaj / niveluri bloc / cotă indiviză | — | ● | — | — | — | — | — |
| Înălțime liberă / date tehnice | — | — | — | ○ | ● | — | ○ |
| Certificat urbanism (POT/CUT) | ○ | — | ● | ○ | ○ | ○ | ○ |
| Coordonate Stereo 70 | ○ | — | ● | ○ | ○ | ● | ○ |
| Venit (VBP, neocupare, chelt., rată cap.) | — | — | ○ | ● | ○ | ○ | ○ |
| DCF (fluxuri, rată actualizare, reziduală) | — | — | ○ | ○ | ○ | — | ○ |
| Contracte închiriere | — | — | — | ● | ○ | — | ○ |
| Certificat energetic (CPE) | ● | ● | — | ● | ● | — | ● |
| Categorie folosință / bonitate sol | — | — | ○ | — | — | ● | — |
| Scenariu PGA (going concern/OER) | — | — | — | ○ | — | — | ○ |

> **Concluzie pentru produs:** UI-ul deja face toggling pe tip prin `aplicaTip()` (`dosar.html` §827–844),
> dar acoperă doar 5 tipuri și nu condiționează **grila de venit** și **CPE/urbanism** după tip. Tabelul de
> mai sus = harta a ce ar trebui afișat/cerut per tip (vezi Livrabil 3 pentru gap-uri concrete).

---

**Documente conexe:** `docs/SEV-2025-ce-putem-folosi.md` (Livrabil 1), `docs/SEV-2025-gap-implementare.md`
(Livrabil 3), `docs/GEV520-2025-crosscheck.md`.
