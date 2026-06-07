# Acord de nivel de servicii (SLA) — suport Evaluare ANEVAR

> **DRAFT / ȘABLON.** Cadrul procedural de suport cerut de bănci / ANEVAR la evaluarea unui furnizor.
> Valorile între paranteze pătrate `[…]` le stabilește furnizorul (Adi) la lansare. Versiune 2026-06-07.

## 1. Scop și părți
Prezentul SLA descrie nivelul de servicii de **suport tehnic și mentenanță** pentru aplicația „Evaluare
ANEVAR" (instrument software de asistență a evaluării imobiliare, rulat **local** pe stația evaluatorului).
- **Furnizor:** [denumire / PFA / SRL], contact suport: `[email]`, telefon: `[telefon]`.
- **Beneficiar:** evaluatorul autorizat ANEVAR licențiat (sau organizația acestuia).

## 2. Natura serviciului (important)
Aplicația rulează **integral local și offline** pe calculatorul evaluatorului. **Nu există un serviciu
server găzduit de furnizor** care să poată „cădea"; de aceea acest SLA NU exprimă o „disponibilitate de
uptime" în sensul clasic — funcționarea aplicației depinde de stația beneficiarului. SLA-ul acoperă:
remedierea defectelor, suportul la utilizare, livrarea de actualizări și răspunsul la incidente.

## 3. Canale și program de suport
- **Canal principal:** e-mail `[email-suport]` (ticket).
- **Program:** [L–V, 09:00–18:00, exclus sărbători legale RO].
- Cererile primite în afara programului se înregistrează la următoarea zi lucrătoare.

## 4. Clasificarea severității și timpi-țintă
| Sev. | Definiție | Răspuns inițial (țintă) | Rezolvare / ocolire (țintă) |
|------|-----------|--------------------------|------------------------------|
| **P1 — Critic** | Aplicația nu pornește / calcul greșit reproductibil / pierdere de date / problemă care invalidează un raport | `[4 ore lucrătoare]` | `[1–2 zile lucrătoare]` (patch sau soluție de ocolire) |
| **P2 — Major** | Funcție importantă nefuncțională, dar există ocolire (ex. descoperire portal indisponibilă) | `[1 zi lucrătoare]` | `[5 zile lucrătoare]` |
| **P3 — Minor** | Defect cosmetic, întrebare de utilizare, cerere de îmbunătățire | `[2 zile lucrătoare]` | versiunea planificată |

> Timpii sunt **ținte de efort**, nu garanții contractuale ferme, până la stabilirea lor de furnizor.

## 5. Ce este inclus / exclus
**Inclus:** remedierea defectelor reproductibile; suport la instalare și utilizare; livrarea de actualizări
de corecție și conformitate; documentația (manual, note de versiune).
**Exclus:** problemele cauzate de hardware/OS-ul beneficiarului, de modificări neautorizate, de lipsa
internetului pentru funcții online (descoperire/AI), de chei API terțe (Anthropic/Perplexity) sau de date
de intrare eronate; **validarea profesională a conținutului** (rămâne a evaluatorului); consultanța juridică.

## 6. Actualizări și conformitate
- Actualizările se livrează ca **executabil nou** (`.exe`), cu **note de versiune**.
- **Actualizare obligatorie de conformitate:** la o modificare a standardelor (SEV/GEV) sau a legislației
  (Legea 129, GDPR) relevantă pentru corectitudinea raportului, furnizorul anunță și pune la dispoziție o
  versiune actualizată; versiunile depășite pot fi marcate ca atare (kill-switch de versiune — planificat).
- Beneficiarul e responsabil de a rula **versiunea curentă** pentru rapoarte oficiale.

## 7. Date, securitate, continuitate
- Datele rămân **local**, la beneficiar (operator de date GDPR). Backup-ul și protecția discului
  (ex. BitLocker) sunt responsabilitatea beneficiarului — vezi `plan-incident-breach.md`.
- Aplicația păstrează **versiuni** ale fiecărui raport în folderul dosarului (recuperare locală).
- Incidentele de securitate/breșe se tratează conform `plan-incident-breach.md` (notificare GDPR).

## 8. Limitări de răspundere
Aplicația **asistă**; nu înlocuiește evaluatorul și nu decide valoarea. Răspunderea profesională pentru
raport aparține evaluatorului autorizat ANEVAR. Răspunderea furnizorului se limitează la `[…]` conform
contractului de licență (EULA, `docs/legal/12-acord-licenta-EULA-DRAFT.md`).

> A se valida cu jurist înainte de utilizare contractuală.
