# SEV 2025 — gap de implementare (cerințe vs. cod) (LIVRABIL 3)

> **Cerința Adi:** „identifică dacă am implementat corect anumite feature-uri sau dacă am sărit features".
> Acest document compară cerințele cheie ale SEV 2025 cu ce **face efectiv** aplicația (engine, assembler,
> report/generator, web/routers, templates), cu evidență `fișier:linie`. Prioritizat pe ce e **BLOCANT**
> pentru un raport conform **GEV 520** acceptabil de bancă.
>
> **Domeniu:** fluxul casă+teren / garantare credit + celelalte tipuri din `profil.py`.
> **Complementar cu** `docs/GEV520-2025-crosscheck.md` (acel doc acoperă în detaliu **conținutul de raport
> GEV 520**; aici extindem la **GEV 630 / SEV 230 / per-tip / motor de calcul** și nu repetăm punctele
> deja tratate acolo — le referențiez ca [crosscheck #N]).
>
> Stare: ✅ implementat corect · 🟡 parțial · 🔴 lipsă · ⛔ greșit/contradicție
> Severitate: **B** = blocant pentru acceptare bancă · **M** = mediu · **m** = minor

---

## 0. Ce e SOLID (implementat corect) — ca să nu reparăm ce merge

| Cerință SEV 2025 | Cod | Stare |
|---|---|---|
| 3 abordări cu ieșire comună + reconciliere pe profil | `engine/abordari.py`, `engine/reconciliation.py:78` | ✅ |
| **Interdicția mediei aritmetice** între abordări (GEV 630 §107) | reconcilierea selectează/ponderează explicit, nu mediază orb; nota de transparență la excludere `reconciliation.py:107–113` | ✅ |
| Min 3 comparabile (GEV 630 §51) | `engine/validation.py:54` (configurabil M5) | ✅ |
| Praguri ajustare brută / outlier / preț corectat ≤0 | `engine/validation.py:50–127` (piață + teren simetric) | ✅ |
| Depreciere fizică/funcțională/externă + justificare obligatorie | `engine/cost.py:50`, `engine/validation.py:130` | ✅ |
| **SEV 450 asigurare** = cost de reconstrucție brut (CIB), fără teren | `assembler.py:206–211`, `profil.py:58` | ✅ |
| Tip valoare + **sursa definiției** (SEV 102 §20.4 / SEV 106) | `report/generator.py:108–128` | ✅ |
| Declarația SEV 100 (scepticism + verificarea calității) | `report/generator.py:261–265` | ✅ |
| Ipoteză transfer liber pentru bun ocupat de proprietar (GEV 520 A8) | `report/generator.py:300–310` | ✅ [crosscheck #19] |
| **BIG condiționat de ANAF** (GEV 520 §78) | `report/generator.py:555–566`, `models/meta.py:19` | ✅ (rezolvat de la crosscheck #23) |
| Cei 4 factori de performanță a garanției (GEV 520 A5 a–d) | `report/generator.py` risc garanție | ✅ [crosscheck #11–14] |
| Inspecție: amploare + însoțitor + observații capturate | `models/meta.py:32–34`, `report/generator.py:771–780` | ✅ (rezolvat de la crosscheck #7–8) |
| Set documente: act + CF + sarcini + CPE-câmp | `models/meta.py:22–26`, `dosar.html:144–164` | 🟡 (CPE nu e câmp dedicat — vezi G7) |

---

## 1. GAP-uri BLOCANTE pentru acceptare bancă (severitate B)

### G1 ⛔/🔴 — Secțiune ESG lipsă (riscuri fizice + certificat energetic) **[B]**
**Cerință:** GEV 520 §86–88 (novație 2025): raportul de garantare trebuie să trateze factorii ESG —
**riscuri fizice** (cu disclaimerul „calitatea de evaluator autorizat nu oferă competență de cuantificare")
și **certificatul energetic** (analizat sau menționat că nu există evidențe de piață).
**Cod:** ESG apare DOAR ca o frază în termenii de referință — `report/generator.py:343`. **Nu există secțiune
ESG dedicată** și niciun câmp de risc fizic / CPE în `models/meta.py`.
**Stare:** 🔴 lipsă. **De ce blochează:** băncile EBA-compliant cer tratarea ESG; un raport 2025 fără ESG e
formal neconform GEV 520. **Acțiune:** `_adauga_esg()` pe profil `GEV_520` + câmpuri meta (risc fizic,
CPE). [crosscheck #24–26]

### G2 🔴 — Tipul „comercial" + abordarea prin VENIT nereprezentate în UI **[B pentru comercial]**
**Cerință:** GEV 630 §59–71 + GEV 232 §11: proprietățile generatoare de venit se evaluează **principal prin
venit**. GEV 520 §67.a le exclude de la evaluarea globală → necesită evaluare individuală cu venit.
**Cod:** Motorul de venit/DCF **există și e wired** (`assembler.py:195–238`, `engine/venit.py`), iar
`profil.py:39` definește `COMERCIAL_INCHIRIAT`. **DAR** dropdown-ul `tip_proprietate` din
`dosar.html:127–130` expune doar casa/apartament/industrial/agricol/special — **„comercial" lipsește**, și
`assembler.py:46 PROFIL_DUPA_TIP` nu mapează „comercial". Grila de chirii (`dosar.html:336`) există dar nu
calculează automat VBP din ea.
**Stare:** 🟡 motor da / 🔴 inaccesibil din UI. **De ce blochează:** un evaluator nu poate produce din UI un
raport pe venit pentru un spațiu comercial — exact cazul unde venitul e obligatoriu.
**Acțiune:** adaugă „comercial" în dropdown + mapare în `PROFIL_DUPA_TIP`; leagă grila de chirii la `date_venit`.

### G3 🔴 — Garda „cost ≠ abordare principală la garantare" lipsește **[B]**
**Cerință:** GEV 520 §31: la bunuri imobile, abordarea prin cost **nu** trebuie folosită ca principală
(lichiditate); §34: cost devine relevant doar la lipsă piață+venit, **cu accept scris** al creditorului.
**Cod:** `assembler.py:231` acceptă tăcut `metoda="cost"` ca primară pe profil `GEV_520`, fără nicio alertă.
`engine/validation.py` nu are nicio verificare pe relația metodă↔ghid.
**Stare:** 🔴 lipsă. **De ce blochează:** un raport de garantare cu valoarea pe cost ca principală, fără
justificarea §34, e respins de verificarea ANEVAR/bancă.
**Acțiune:** validator nou `valideaza_metoda_vs_ghid(profil, metoda)` → alertă pe `GEV_520 + metoda=cost`.

### G4 🔴 — Declarația de conflict de interese / EBA + plata necondiționată **[B]**
**Cerință:** GEV 520 §81 (declarații exprese privind lipsa conflictului de interese, **inclusiv cerințele
EBA**) + §82 (plata serviciului **nu** e condiționată de acceptarea garanției).
**Cod:** Declarația de conformitate (`report/generator.py:245–265`) acoperă independența SEV 100, dar **nu**
menționează EBA / conflictul de interese distinct, nici plata necondiționată.
**Stare:** 🔴 lipsă. [crosscheck #5, #6]. **Acțiune:** 2 fraze în declarația de conformitate pe profil GEV_520.

---

## 2. GAP-uri de severitate MEDIE (M)

### G5 🟡 — Recipisă BIG: textul spune „se înregistrează", nu evidențiază **recipisa** **[M]**
**Cerință:** GEV 520 §83–84: raportul final conține **dovada scrisă (recipisa)** de înregistrare în BIG.
**Cod:** `report/generator.py:564–566` afirmă „se înregistrează în BIG", fără a marca recipisa ca anexă
obligatorie. **Stare:** 🟡 [crosscheck #21]. **Acțiune:** punct de checklist + anexă „recipisă BIG".

### G6 🔴 — Re-desemnarea utilizatorului (raport pt alt scop ≠ utilizabil la garantare) **[M]**
**Cerință:** GEV 520 §7 + §4: un raport întocmit pentru alt scop NU poate fi folosit de creditor pentru
garantare fără re-desemnarea utilizatorului + modificarea înregistrării BIG.
**Cod:** nicăieri. **Stare:** 🔴 [crosscheck #22]. **Acțiune:** notă în termeni + punct de checklist.

### G7 🟡 — Certificat energetic (CPE) nu e câmp dedicat în setul de documente **[M]**
**Cerință:** GEV 520 §46: „certificatul energetic al fiecărei clădiri subiect" e document obligatoriu.
**Cod:** `models/meta.py` nu are câmp CPE; `dosar.html` nu îl cere. **Stare:** 🟡 [crosscheck #10].
**Acțiune:** câmp `certificat_energetic` în meta + în setul de documente raportat.

### G8 🟡 — Analiza pieței / aria de piață e text liber „[de completat]", nu structurată **[M]**
**Cerință:** GEV 630 §30–34: analiza de piață **obligatorie**, individualizată, cu delimitarea ariei de piață
și suport pentru elementele abordărilor (chirii, neocupare, rate cap., prețuri).
**Cod:** Capitolul 3 „PREZENTAREA DATELOR DE PIATA" (`report/generator.py:735–740`) e doar narativ AI sau
placeholder „Analiza pietei locale [de completat]". Nu există câmpuri structurate (aria de piață, tendințe).
**Stare:** 🟡 prezent ca shell, nestructurat. **Acțiune:** câmpuri minime de analiză de piață per tip.

### G9 🟡 — Metoda reziduală / parcelare pentru teren — neimplementate **[M pentru teren/special]**
**Cerință:** GEV 630 §82, §97–102: teren liber poate cere extracție, alocare, **metoda reziduală**
(autorizație de construire), capitalizarea rentei funciare, analiza parcelării (DCF).
**Cod:** `engine/land.py` implementează DOAR comparația vânzărilor (grilă EUR/mp). Celelalte metode lipsesc.
**Stare:** 🟡 acoperă cazul comun (comparația = §83 „cea mai adecvată"), dar nu cazurile fără comparabile.
**Acțiune:** la prioritate joasă; relevant la teren de dezvoltare / special.

---

## 3. GAP-uri MINORE (m) / observații

| # | Observație | Cerință | Cod | Stare |
|---|---|---|---|---|
| G10 | Scopuri `vanzare`, `expropriere`, `aport` definite în `profil.py:10` dar lipsesc din dropdown `scop` | — | `dosar.html:122–126` | 🟡 m |
| G11 | „A doua abordare formală" (GEV 630 §108, GEV 520 §32) nu e detectată (pondere ~0 pe a doua) | GEV 630 §108 | `assembler.py:237` | 🔴 m |
| G12 | Ierarhia datelor de intrare SEV 104 / SEV 230 §100.2 (comparabil direct/indirect/general) nu e metadată pe comparabile | SEV 104 | `models/comparable.py` | 🔴 m |
| G13 | Chirie peste piață (GEV 520 A6) — fără notă de risc | GEV 520 A6 | — | 🔴 m [crosscheck #15] |
| G14 | PGA — scenariu de bază (going concern/OER) la comercial/special | GEV 520 A9, GEV 232 | — | 🔴 m [crosscheck #16] |
| G15 | Active epuizabile — durata de viață + rata de diminuare (GEV 520 A10) | GEV 520 A10 | — | 🔴 m [crosscheck #17] |
| G16 | Coordonate Stereo 70 la teren (GEV 520 §52) — nu sunt câmp | GEV 520 §52 | — | 🔴 m |
| G17 | DCF: corelarea tip venit↔tip rată (GEV 630 §64, nou 2025) nu e validată | GEV 630 §64 | `engine/venit.py` | 🟡 m |

---

## 4. Prioritizare — ce reparăm pentru un raport GEV 520 acceptabil de bancă

**🔴 Blocante (de făcut înainte de a duce un raport la bancă):**
1. **G1 — secțiune ESG** (riscuri fizice + CPE, cu disclaimer de competență). *Cel mai mare gol normativ 2025.*
2. **G3 — garda cost ≠ principal la garantare** (alertă pe `GEV_520 + metoda=cost`).
3. **G4 — declarație conflict de interese / EBA + plata necondiționată.**
4. **G2 — tipul „comercial" + venit accesibil din UI** (blocant pentru proprietăți generatoare de venit).

**🟠 Importante (întăresc conformitatea, nu blochează un dosar rezidențial simplu):**
5. G6 — re-desemnare utilizator; G5 — recipisă BIG; G7 — câmp CPE; G8 — analiză de piață structurată.

**🟡 Ulterior (cazuri de nișă):**
6. G9 (metode teren), G11–G17 (formal/PGA/epuizabile/Stereo70/data hierarchy).

> **Notă de încredere:** punctele marcate [crosscheck #N] sunt deja documentate în
> `docs/GEV520-2025-crosscheck.md` cu propuneri concrete de cod (secțiunea 4 a acelui document). Acolo unde
> apar diferențe, acest Livrabil 3 reflectă **starea curentă a codului** verificată la data analizei
> (ex. G_BIG/ANAF și inspecția au fost între timp rezolvate față de crosscheck).

---

**Documente conexe:** `docs/SEV-2025-ce-putem-folosi.md` (Livrabil 1), `docs/SEV-2025-cerinte-per-tip-imobil.md`
(Livrabil 2), `docs/GEV520-2025-crosscheck.md`.
