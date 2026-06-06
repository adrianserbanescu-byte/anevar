# Council Review #2 — decizia de lansare comercială (2026-06-06)

> Rulare proaspătă a LLM Council pe **starea curentă** (nu cea veche de 176 MB din primul review),
> pe întrebarea: *care e singurul lucru cel mai probabil să provoace eșecul lansării și unde
> greșește planul în 4 porți?* Membri: gpt-5.1, gemini-3.1-pro, claude-sonnet-4.5, grok-4.3,
> hermes-4-14b. Audit-ul meu (Claude Opus) e în [`00-SINTEZA-lansare-pentru-Adi.md`](00-SINTEZA-lansare-pentru-Adi.md) §5.

## Sinteza chairman-ului (gemini-3.1-pro)

**SINGURUL factor critic de eșec:** Respingerea în bloc a rapoartelor de către departamentele de
**Risc + Securitate IT + Conformitate** ale băncilor (NU departamentele lor de evaluare), declanșată
de **„delegarea mascată"** a deciziei către un gateway AI extern. Dacă o singură bancă pune pe
blacklist un raport (suspiciune de „halucinație AI" care afectează LTV), evaluatorii reziliază instant.

**Unde greșește planul:** cere validarea băncilor (Poarta 0) **înaintea** finalizării logicii
matematice ANEVAR (Poarta 2) și a gardurilor tehnice (Poarta 1). Nu poți cere unei bănci să auditeze
un produs a cărui metodologie nu e finalizată.

**Ce subevaluează echipa:**
1. **Iluzia pseudonimizării:** suprafață exactă + an + etaj + microzonă = amprentă care re-identifică
   banal garanția și clientul → încalcă NDA-urile evaluatorului cu băncile.
2. **Cadrul de răspundere e operațional, nu doar tehnic:** „om în buclă" nu previne litigiile fără
   **audit trail inalterabil** + asumare explicită (override/accept) în UI.

**Reordonare obligatorie propusă de consiliu:**
1. (fosta P2) Finalizarea absolută a logicii ANEVAR (selecție + ajustări).
2. (fosta P1) Garduri tehnice + matricea juridică a deciziei (loguri explicite de asumare în UX).
3. (fosta P0) **Pilot Sandbox cu O SINGURĂ bancă** (depts. Risc + IT, nu doar evaluatori seniori) +
   aviz de la **asigurătorul de răspundere profesională ANEVAR**.
4. (fosta P3) Comercializare.

## Puncte individuale notabile
- **gpt-5.1 (rank 1):** riscul nu e tehnologia, ci **cadrul de răspundere contractual/procedural**.
  Lipsesc din cele 4 porți: proceduri interne de utilizare, manual de bune practici, training
  documentat, SLA suport, plan de incident & breach. Definește-le ÎNAINTE de Poarta 0.
- **gemini (rank 1):** băncile se supun normelor **prudențiale BNR privind riscul IT și
  externalizarea**; gateway AI extern → alerte roșii. Băncile nu fac „peer-review", ele **auditează
  furnizori de risc**.
- **claude-sonnet-4.5:** asigurătorii de răspundere profesională pot **refuza acoperirea** pentru
  rapoarte asistate AI → fără ancorare instituțională fermă, „produs tehnic perfect, comercial mort".
- **grok-4.3:** validare bancară pe **20-30 dosare reale** cu istoric de respingeri, ÎNAINTE de
  orice gateway; risc de **răspundere solidară** (evaluator + editor AI) + excludere din asigurarea
  de malpraxis ANEVAR.

## Leaderboard (peer-ranking)
1. gpt-5.1 — 1.5 · 2. gemini-3.1-pro — 1.5 · 3. grok-4.3 — 3.25 · 4. claude-sonnet-4.5 — 3.75
