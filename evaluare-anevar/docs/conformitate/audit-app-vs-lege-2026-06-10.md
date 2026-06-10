# Audit APLICAȚIE vs LEGE / NORME / LEGISLAȚIE NOUĂ — raport pentru Adi (2026-06-10)

> Declanșat de gate: auditul de **user-journey** a găsit o recomandare MAJORĂ → conform cererii tale, s-a rulat auditul de conformitate app-vs-lege/norme. READ-ONLY (gap-uri identificate, nu modificate — metodologia/juridicul rămân decizia ta + a juristului).

## Verdict de ansamblu
**Aplicația e în mare parte CONFORMĂ** — fără erori aritmetice sau de praguri legale; bazele valorii, abordările și matricea tip×scop sunt corecte. **DAR nu e „turnkey" pentru lansare pe garantare bancară:** există 2 gap-uri P0 + 3 noutăți GEV 520 ed. 2025 absente + itemii AML/GDPR care rămân corect pe calea critică a juristului.

## 🔴 P0 — gap-uri de conformitate reală (risc juridic/profesional)
1. **Declarația de conformitate NECONDIȚIONATĂ.** Standardul cere ca declarația să reflecte eventualele abateri/limitări; acum se emite necondiționat. → **owner: B (metodologie) + decizia ta.** (Notă: se leagă de munca recentă de disclaimer — de verificat dacă disclaimer-ul UI/raport acoperă deja sau trebuie condiționată declarația în sine.)
2. **PII în clar „at rest"** (CNP, nume, adrese în `date/`/foldere). → **owner: jurist + tu** (encryption-at-rest: BitLocker/SQLCipher/disclaimer). **Deja deferat pre-lansare** în tracker — reconfirmat ca P0 de conformitate.

## 🟠 3 noutăți GEV 520 ed. 2025 ABSENTE (garantare credit)
3. **Disclaimer ESG / risc fizic + competență** — GEV 520 2025 cere abordarea riscului ESG/fizic + declarație de competență. → owner: B (metodologie) + jurist.
4. **Re-desemnarea utilizatorului** (user re-designation) — mecanism cerut de ediția nouă. → owner: B (+ leagă de #4 GEV520 `utilizator_desemnat` deja notat ca defer P2).
5. **Declarația de conflict EBA** (conflict of interest, ghidul EBA pe evaluări pentru garantare). → owner: B (metodologie) + jurist.

## AML / GDPR — rămân la JURIST (cale critică validare externă)
- AML (Legea 129/2019 + Norme ONPCSB): textul juridic + listele = bucket C (jurist). Hardening-ul de input al endpoint-ului AML (eroarea 500 găsită de D) = rezolvat separat ca robustețe.
- GDPR: temei legal, retenție, DSAR/ștergere, notă de informare, PII `proprietar` → jurist.

## Concluzie + recomandare A
Nimic **aritmetic/de calcul** nu e greșit (motorul e solid, confirmat de re-auditurile anterioare). Gap-urile sunt de **conformitate documentară + juridică** — exact zona pe care filozofia aplicației o lasă evaluatorului senior (bucket B) + juristului (bucket C). **NU sunt de competența mea să le „repar" unilateral** (aș schimba metodologia/textul juridic). Le **escaladez ție** pentru decizie + dispatch către B (noutățile GEV 520) și jurist (AML/GDPR/PII/declarații).

**Pentru lansare sigură pe garantare:** P0#1 (condiționarea declarației) + noutățile GEV 520 = de implementat cu B/jurist; P0#2 (PII-at-rest) + AML/GDPR = de validat cu juristul. Restul app-ului e gata.
</content>
