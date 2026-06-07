# Digest — Răspuns LLM Council „Descoperă" (2026-06-07)

> Sinteza acționabilă a răspunsului council (raw complet în `council-raspuns.md`).
> Panel: **GPT-5.1** · **Claude Sonnet 4.5** · **Gemini 3.1 Pro** (chairman) · **Grok 4.3**.

## Leaderboard (peer-ranking, mai mic = mai bun)
1. **gpt-5.1** — 1.5 (cel mai bine cotat)
2. **claude-sonnet-4.5** — 1.75
3. **gemini-3.1-pro** — 2.75 (chairman)
4. **grok-4.3** — 4.0 (cel mai scurt, a lăsat întrebări nedezvoltate)

---

## Q1 — Criterii + ponderi per categorie
Premisă contestată: similaritatea liniară pură e deficitară — există **„Value Cliffs"** (praguri abrupte; ex. an < 1977 vs > 1977 = înainte/după cutremur). Strategie în 2 pași: **(1) Filtru de eligibilitate** (must-have-uri, triază) + **(2) Scor de similaritate**.

- **#1 Casă+teren (revizuit):** Suprafață **×6**, **Teren ×5** (×1 actual e prea mic — în RO valoarea casei depinde de teren), An ×4 (trepte decadale/cutremur), Stare(LLM) ×2, Finisaj(LLM) ×1, Nr. camere ×2 (promovat din metadata).
- **#2 Apartament — „EXTREM DE URGENT" (60–70% din piață):** filtru obligatoriu ±1 cameră. Scoring: Suprafață **×7**, **Etaj ×5** (neliniar: etaj intermediar 3 vs 4 → d=0.1; Parter/Ultimul vs intermediar → d=0.7), **Nr. camere ×4**, An ×3, Stare ×2.
- **#3 Industrial:** „NU prioritizați scoringul încă — aveți nevoie de DATE." Parser pe VDI.ro + Imoradar24. Ulterior: Suprafață ×5, Înălțime liberă ×5, Acces TIR ×4, Trifazic/utilități ×3.
- **#4 Teren agricol:** Suprafață **×5 logaritmic** (500→1000mp ≠ 15.000→15.500mp), Deschidere la drum/acces ×4, Categorie folosință (arabil/pășune) ×4.
- **#5 Special (catch-all):** nu se poate un scor numeric universal → abordare **semi-manuală**: userul alege axele relevante (capacitate/vitrină/etc.), similaritatea se calculează doar pe ele.

**Risc LLM (stare ×4 + finisaj ×3):** scade ponderile, badge **„⚠️ Estimat de AI"** + buton **Confirmare manuală** (după validare → revine la pondere maximă).

## Q4 — Distanța în ranking
**NU în scorul procentual direct** (pin-urile de pe agregatoare sunt fuzzy; ai face scorul inutilizabil). Context-dependent:
- Apartamente/Case în orașe mari: **tie-breaker / penalizare separată** afișată („Scor 90% (−15% distanță 3km, alt cartier)").
- Industrial/Teren: distanța **față de infrastructură** (autostradă, drum betonat, CF), nu față de subiect.
- Implementare: **OSM România + SIRUTA + geocoding offline (PostGIS/Nominatim)** — ~2–3 zile, cost ulterior zero.

## Q5/Q7 — Model extracție + discovery + consiliu API
- **Extracție:** mută pe model ieftin JSON-strict — **Llama 3.3 70B / Gemini Flash** (diferență factuală nulă vs Claude, ~10× mai ieftin); Claude doar **fallback** la confidență scăzută.
- **Discovery:** search-urile tip Perplexity = groaznice pe real-estate RO. Soluție: **parser Imoradar24** (doar discovery) → urmează redirect-ul → scrape sursa originală.
- **Consiliu de API:** respins ca generic (3× cost/latență, gain marginal). *Excepție Claude:* votare 2/3 cu modele ieftine **doar pe câmpuri critice** (stare, intravilan/extravilan = „10× diferență preț").

## Q9 — Ce ne scapă (premise contestate)
1. **Lipsă Ground Truth** — nicio metrică de succes. Pune sistemul în fața a 5 evaluatori ANEVAR, loghează **ce RESPING** din listă (Overlap@5 target >60%).
2. **Decay temporal** — anunț vechi de 8 luni ≠ de ieri; penalizare de vechime pe preț.
3. **Formatul de ieșire** — lipsește „**Exportă Comparabile ANEVAR**" (tabel Subiect vs Candidați + justificare generată). „Dacă userul face copy-paste manual, n-ai inovat procesul, ai făcut doar un search mai deștept."

## Q10 — Cea mai inovatoare idee (3 direcții diferite în panel)
- **Vision-Language pe foto** (Gemini/chairman): scrape primele 3 imagini + VLM „dă scor structural 1–5, **ignoră descrierea agentului**" — pentru că „stare/finisaj" din textul agentului („superb", „renovat") e sursa masivă a erorilor. Lansare ca „X-Ray Scan Premium". Risc: cost procesare imagini.
- **Copilot care învață din respingere** (GPT-5.1): când evaluatorul alege Rank 5 și ignoră primele 4, antrenezi un model ușor → `score = α·reguli + (1−α)·învățat` → **lock-in** per evaluator.
- **„Piață Sintetică" — graf de proprietăți** cu propagare de preț (Claude, NetworkX/Neo4j + vizualizare 3D).
- (Grok: embeddings + nearest-neighbor pe graf.)

## Q8 — Prioritizare (chairman)
- **P0 (1–2 sprinturi):** decuplează modelul de casă + scoring Apartament #2; reduce pondere AI + flow confirmare; switch LLM ieftin.
- **P1 (săpt. 3–6):** parser VDI.ro (deschide #3); geocodare offline.
- **P2:** Export ANEVAR Standard (killer feature retenție); Imoradar24 pentru sate.

## Q2 / Q3 / Q6 (secundare)
- **Q2:** criteriile secundare = **„Boosters"** transparente („Am găsit Lift. Confirmă pentru +10%").
- **Q3:** praguri — sate/comune: localitate; orașe <50k: cartier; orașe mari: sub-zonă/rază. „Primăverii vs Pantelimon = obiecte economice diferite."
- **Q6:** OLX scos din ranking; păstrat doar pentru „sanity-check preț/mp pe zonă" lateral.

---

## Dezacorduri notabile (semnal valoros)
1. **Pondere Teren #1:** Gemini/chairman ×5 · Claude ×3 (log) · Grok ×2 · GPT-5.1 cel mai mic (~0.1) — toți: ×1 actual e greșit, dar valoarea diferă.
2. **Distanța în scor:** Grok = DA (tie-breaker mic); restul = NU (badge separat).
3. **Consiliu API:** majoritar NU; Claude = DA chirurgical (2/3 doar pe câmpuri critice).
4. **Scorul 0–100% însuși:** Claude & GPT îl contestă — vor **radar chart pe 3–4 axe** (Locație/Fizic/Calitate/Funcțional), nu un singur %.
5. **Pivot radical (doar Claude):** acces la **tranzacții reale ANCPI/notariat** (preț FINAL) vs anunțuri (preț ASK +10–15%) — „strat 0".

## TOP 5 acțiuni (consens 4/4)
1. **Decuplează modelul de casă + scoring Apartament #2** (Etaj ×5, Nr. camere ×4, filtru ±1 cameră) — din atribute deja extrase, nefolosite.
2. **Redu riscul LLM** pe stare/finisaj (pondere mai mică + badge „⚠️ AI" + confirmare manuală).
3. **Switch extracție pe model ieftin** (Llama 3.3 70B / Gemini Flash, ~10× mai ieftin; Claude fallback).
4. **Extinde acoperirea #3/#5** (parser VDI.ro + Imoradar24) înainte de scoring fin — „acoperirea > acuratețea acum".
5. **Geocodare offline** (OSM + SIRUTA + PostGIS) — distanță ca tie-breaker, nu în scor.

**Goluri critice subliniate:** Ground Truth (validare cu evaluatori), Export raport ANEVAR (.docx/.xlsx), feedback loop + decay temporal.
