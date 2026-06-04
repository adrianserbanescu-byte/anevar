# Fazele 1–7 — Planuri de implementare (structurate) — Platformă de evaluare imobiliară

> **For agentic workers:** Acestea sunt **planuri de fază** (scop · fișiere · sarcini · criterii · dependențe).
> NU sunt încă planuri TDD pas-cu-pas: codul fiecărei faze depinde de **interfețele reale produse de Faza 0**
> (`ProfilEvaluare`, `RezultatAbordare`, `reconcile_profil`, registrul de secțiuni) și, pentru venit, de un
> **dosar real de validare**. La rândul fiecărei faze: se scrie întâi spec-ul ei (dacă aduce decizii noi),
> apoi un plan TDD complet (cu `superpowers:writing-plans`) ancorat în codul existent la acel moment.

**Referință spec:** `docs/superpowers/specs/2026-06-04-platforma-evaluare-imobiliara-master-design.md` (§4).
**Pornesc DOAR după Faza 0** (`2026-06-04-faza0-fundatie.md`).

**Principii la fiecare fază (neschimbate):** aditiv & compatibil înapoi · validat pe dovezi · om-în-buclă ·
GDPR-first · offline · TDD + rebuild + smoke · ancorat în SEV 2025/IVS + GEV.

---

## Faza 1 — Apartament (rezidențial, garantare credit)
**Depinde de:** Faza 0. **Abordări:** comparație (primară) + cost.
**Fișiere (estimat):**
- `src/evaluare/profil.py` — profil predefinit `APARTAMENT_GARANTARE`.
- `src/evaluare/models/property.py` — câmpuri apartament (etaj, nr_niveluri_bloc, an_bloc, cotă teren, regim înălțime) — opționale, compatibile înapoi.
- `src/evaluare/engine/market.py` (sau catalog de grilă) — elemente de ajustare specifice apartamentului (etaj, vechime bloc, tip imobil) — fără a rupe grila casei.
- `src/evaluare/web/templates/wizard.html` — selector „tip proprietate" la Pas 1; câmpurile apartament apar condiționat.
- `report/sectiuni.py` + generator — descriere proprietate adaptată apartamentului.

**Sarcini:**
- [ ] Spec scurt (ce atribute de apartament intră în grilă/raport).
- [ ] Profil `APARTAMENT_GARANTARE` + teste.
- [ ] Câmpuri apartament în model + validări (etaj ≤ niveluri) + teste.
- [ ] Elemente de grilă specifice apartament + regresie (casa neschimbată).
- [ ] UI: selector tip proprietate (casă/apartament) + câmpuri condiționate.
- [ ] Raport: descriere apartament.
- [ ] Suită verde + rebuild + smoke.

**Criterii de acceptare:** o evaluare de apartament prin comparație produce valoare corectă; cazul casă+teren
rămâne identic; raportul reflectă tipul.
**Input necesar:** (opțional) un dosar real de apartament pentru regresie.

---

## Faza 2 — Comercial / închiriat (abordarea prin venit devine primară, GEV 630)
**Depinde de:** Faza 0 (motor venit + secțiuni). **Cea mai mare valoare nouă.**
**Fișiere (estimat):**
- `src/evaluare/profil.py` — `COMERCIAL_INCHIRIAT` (abordări `["venit","comparatie"]`, ghid `GEV_630`).
- `src/evaluare/web/app.py` — endpoint `POST /api/grila-venit` (DateVenit → valoare) + integrare în asamblare.
- `src/evaluare/web/templates/` — UI pentru DateVenit (chirii, neocupare, cheltuieli, rată capitalizare) cu note de sursă (om-în-buclă).
- `src/evaluare/report/generator.py` — **randarea** secțiunii `abordare_venit` (acum doar id în registru) + secțiunile GEV 630.
- `src/evaluare/assembler.py` — rulează abordarea prin venit când profilul o cere; `reconcile_profil`.

**Sarcini:**
- [ ] Spec scurt (GEV 630: conținut obligatoriu pentru imobiliare cu venit).
- [ ] Profil `COMERCIAL_INCHIRIAT` + teste.
- [ ] Endpoint `/api/grila-venit` + teste web.
- [ ] UI introducere venit + afișare NOI/valoare.
- [ ] Integrare în `construieste_context` prin `reconcile_profil` (regresie pe casă+teren).
- [ ] Raport: render secțiune venit + GEV 630.
- [ ] Suită verde + rebuild + smoke.

**Criterii de acceptare:** evaluare comercială prin capitalizare directă produce raport GEV 630 cu secțiunea
de venit; casă+teren neschimbat.
**Input necesar (important):** **dosar real comercial/închiriat** pentru validare (ancorare numerică); textul
GEV 630 oficial.

---

## Faza 3 — Industrial (hală / depozit / logistică)
**Depinde de:** Fazele 0, 2 (venit). **Abordări:** cost (specific) + venit.
**Fișiere (estimat):** profil `INDUSTRIAL`; eventual costuri unitare specifice (structură metalică, deschideri mari);
descriere proprietate industrială.
**Sarcini:**
- [ ] Spec scurt (specific industrial: înălțime liberă, travee, dotări).
- [ ] Profil `INDUSTRIAL` + teste.
- [ ] Ajustări/cost specifice + teste.
- [ ] UI + raport.
- [ ] Suită + rebuild + smoke.
**Criterii:** evaluare industrială cost+venit corectă; restul neschimbat.
**Input necesar:** catalog de costuri pe categorii industriale (vezi blocaj IROVAL); dosar real (opțional).

---

## Faza 4 — Agricol / teren cu destinații
**Depinde de:** Faza 0. **Abordări:** comparație specifică; (opțional) venit agricol (rentă).
**Fișiere (estimat):** profil `AGRICOL`; elemente de grilă pentru teren agricol (clasă de calitate, categorie de
folosință, acces, irigații); eventual capitalizarea rentei agricole.
**Sarcini:**
- [ ] Spec scurt (atribute teren agricol; rentă).
- [ ] Profil + teste.
- [ ] Grilă teren agricol + teste.
- [ ] (opțional) venit din rentă.
- [ ] UI + raport + suită + rebuild.
**Criterii:** evaluare teren agricol corectă; grila de teren existentă neschimbată.

---

## Faza 5 — Scopuri noi (tip de valoare + ghiduri)
**Depinde de:** Faza 0 (registru secțiuni). **Acoperă axa B/C/E a matricei.**
Sub-livrabile (fiecare cu profil + secțiuni proprii):
- [ ] **Raportare financiară IFRS** — valoare justă, ghid `GEV_500`, secțiune `raportare_financiara`.
- [ ] **Asigurare** — valoare de asigurare (cost de reconstrucție), profil + secțiune.
- [ ] **Impozitare** — bază de impozitare.
- [ ] **Litigii / expropriere** — ipoteze speciale, mențiuni de scop.
**Fișiere (estimat):** profiluri noi; secțiuni de raport per ghid; tip valoare per scop (deja în enum din Faza 0).
**Criterii:** fiecare scop produce un raport cu termenii de referință + tipul de valoare + ghidul corecte.
**Input necesar:** textele oficiale GEV 500 etc.; eventual validare juridică pe scopurile sensibile (litigii).

---

## Faza 6 — DCF + grila de chirii (adâncirea venitului)
**Depinde de:** Faza 2.
**Fișiere (estimat):**
- `src/evaluare/engine/venit.py` — `evalueaza_dcf(fluxuri, rata_actualizare, valoare_reziduala)` (flux multi-anual).
- `src/evaluare/engine/chirii.py` — grilă de chirii comparabile (analog grilei de vânzări) → chirie de piață.
**Sarcini:**
- [ ] Spec scurt (DCF: orizont, valoare reziduală, rată de actualizare; grilă chirii).
- [ ] `evalueaza_dcf` + teste (exemple deterministe).
- [ ] Grilă chirii + teste.
- [ ] UI + raport (tabel flux) + suită + rebuild.
**Criterii:** DCF reproduce un exemplu cunoscut; chiria de piață rezultă din grilă.
**Input necesar (important):** dosar real cu DCF pentru validare.

---

## Faza 7 — Special (hotel, benzinărie etc.)
**Depinde de:** Fazele 2, 6. **Cazuri complexe, nișă.**
**Fișiere (estimat):** profil `SPECIAL`; metode specifice (ex. metoda profitului pentru hotel); secțiuni dedicate.
**Sarcini:**
- [ ] Spec per tip special (decizii metodologice).
- [ ] Implementare metodă specifică + teste.
- [ ] UI + raport + suită + rebuild.
**Criterii:** cel puțin un tip special evaluabil end-to-end.
**Input necesar:** expertiză/decizii metodologice + dosare reale; probabil ultimul de făcut.

---

## Rezumat dependențe & ordine
```
Faza 0 (fundația) ── Faza 1 (apartament)
                  ├─ Faza 2 (comercial/venit) ── Faza 3 (industrial)
                  │                            ├─ Faza 6 (DCF+chirii) ── Faza 7 (special)
                  ├─ Faza 4 (agricol)
                  └─ Faza 5 (scopuri noi)
```
**Blocaje externe transversale** (nu opresc fundația): catalog IROVAL (Faza 3), dosare reale de validare
(Fazele 2/6), texte oficiale GEV 500/630 (Fazele 2/5), validare juridică (Faza 5 litigii).
