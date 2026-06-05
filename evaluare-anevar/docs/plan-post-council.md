# Plan post-review LLM Council

Triaj al feedback-ului consiliului (vezi `review-llm-council-RESULT.md`) + backlog-ul intern,
repartizat pe categorii. **Regulă:** nu se modifică metodologia de evaluare sau praguri legale
fără validare umană (evaluator senior / jurist). Aplicația doar **avertizează** evaluatorul.

---

## 🟢 A. Garduri de protecție — implementate în cod (doar alerte/avertismente, calcule neatinse)

1. Alerte prudențiale de ajustare în grile: linie >15%, brută totală >25–30%, netă >15%.
2. Afișarea **ajustării brute TOTALE** (etapa tranzacție + proprietate) lângă selecție.
3. Alertă consistență cost↔piață: depreciere implicită |construcții−CIN|/CIN > 20% → notă obligatorie.
4. Avertisment „prețuri din OFERTE, nu tranzacții" (descoperire/import) + reamintire ajustare ofertă→tranzacție.
5. AML: banner „NU verifică PEP/sancțiuni — verifică manual [linkuri oficiale]" pe pagină + în .docx;
   disclaimer Art. 33 + bifă de confirmare înainte de RTS/RTN.
6. GDPR: filtru-plasă regex (CNP/CF/adrese) pe textul trimis la AI + notă despre ce se trimite.
7. AI narativ: temperatură joasă + „nu inventa surse" + marcaj „draft AI — verifică".
8. Avertisment dacă baza SQLite e într-un folder de sync cloud (OneDrive/Dropbox → „database locked").

---

## 🟡 B. De VALIDAT cu un evaluator autorizat ANEVAR (metodologie/domeniu — nu se ating fără confirmare)

Din consiliu:
- **B1.** Grila casă/apartament: prezentare pe **€/mp corectat** (matematica e echivalentă; e doar
  forma așteptată de bănci). De adăugat ca strat de prezentare în grilă + raport.
- **B2.** Criteriul de **selecție pe ajustarea brută TOTALĂ** (nu doar etapa de proprietate) — de
  confirmat dacă devine criteriul principal sau rămâne secundar.
- **B3.** Ajustare **degresivă de suprafață** pentru diferențe mari (>20–25%), nu liniară.
- **B4.** **Valoarea de lichidare / vânzare forțată** (GEV 520 §6.4).
- **B5.** **Anexa 1 — certificarea conformității** (checklist ~18 puncte) + **grilă de risc garanție**
  (lichiditate, vandabilitate, risc juridic/tehnic) cu scor.
- **B6.** Fundamentarea **ratei de capitalizare/actualizare** (extragere din tranzacții + citare sursă);
  bază locală de rate.
- **B7.** Secțiune explicită **HBU / cea mai bună utilizare** + analiză de piață locală (trend, lichiditate, timp de expunere).
- **B8.** Prag KYC numerar: de confirmat **3.000 € (ocazional) vs 10.000 €** și logica de praguri (cu jurist — vezi C).

Din backlog-ul intern (necesită decizie metodologică):
- **B9.** Metode specializate prin **profit** pentru hotel / benzinărie (proprietăți cu exploatare specifică).
- **B10.** Secțiune dedicată **GEV 500** (valoarea impozabilă a clădirilor) pentru scopul de impozitare.

---

## 🔴 C. Activități EXTERNE (terți / plătit / acces ANEVAR / juridic / manual)

Din consiliu:
- **C1.** **Audit juridic AML** (avocat specializat Legea 129/2019) — texte RTS/RTN, logica de risc,
  praguri, indicatori. **Blocant absolut înainte de uz real.**
- **C2.** **Peer-review metodologie** de la ≥2 evaluatori seniori + test pe 5–10 dosare reale (aplicație vs. manual).
- **C3.** **Validare cu băncile** — trimite raport demo la 2–3 bănci pentru cerințele lor de formă.
- **C4.** **Certificat code-signing** (~150–300 €/an) — elimină SmartScreen + fals-pozitivii antivirus.
- **C5.** **Pachet GDPR** revizuit juridic (politică, consimțământ, registru) — aplicația poate genera draftul (B), juristul îl validează.
- **C6.** Migrarea **scraping → extensie de browser** (utilizatorul navighează manual, extensia trimite DOM la localhost). Termen scurt: disclaimer + rate-limiting.

Din backlog-ul intern (blocat extern):
- **C7.** Catalog **IROVAL** (costuri unitare €/mp pe categorii) — acces/plată ANEVAR.
- **C8.** Integrare **BIG** (Baza Imobiliară de Garanții) — sursă primară de comparabile confirmate.
- **C9.** Integrare **ANCPI** (carte funciară / cadastru online).
- **C10.** Contribuție automată la BIG/BIF din rapoarte.
- **C11.** **Liste AML live** (sancțiuni UE/ONU, PEP) — OpenSanctions (gratuit) sau World-Check (plătit).
- **C12.** **Transmiterea electronică** la ONPCSB (rapoarte.onpcsb.ro) — o face evaluatorul.
- **C13.** Testare **extracție LLM pe anunțuri reale** (necesită cheie AI activă).
- **C14.** Testare manuală **accesibilitate** (NVDA + reflow 320px / zoom 200%).

---

## 🔵 D. Alte dezvoltări propuse de mine (robustețe/mentenanță — opționale, fără blocaj extern)

- **D1.** **Backup automat** al dosarelor (export JSON/ZIP cu rotație) + buton Backup/Restore.
- **D2.** **Migrare de schemă DB** (versiune + upgrade la pornire), ca să nu se piardă date între versiuni.
- **D3.** **Notificare de versiune nouă** la pornire (verifică GitHub Releases; nu auto-update complet).
- **D4.** **Abstracție `AIProvider`** (interfață → Anthropic/Perplexity), switch fără rescriere.
- **D5.** Optimizare dimensiune `.exe` (excludere coduri Pillow nefolosite → posibil sub 100 MB).
- **D6.** Export **PDF** direct (acum Word→PDF manual) — opțional, decis anterior „nu e cazul".
