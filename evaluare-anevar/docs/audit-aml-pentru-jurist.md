# Dosar pentru auditul juridic AML

**Scop:** material gata de înmânat unui avocat/consultant specializat AML (Legea 129/2019)
pentru validarea modulului AML al aplicației. Conține: ce generează aplicația, temeiul legal
invocat și **întrebările deschise** care necesită decizie juridică. (Punctul C1 din plan.)

> ⚠️ Până la validare, modulul AML afișează deja avertismente („draft neverificat juridic",
> „NU verifică automat PEP/sancțiuni") și cere confirmare înainte de RTS/RTN.

## 1. Cadrul legal pe care se sprijină modulul
- **Legea nr. 129/2019** privind prevenirea spălării banilor și finanțării terorismului.
- **Normele ONPCSB** aprobate prin **Ordinul nr. 37/2021**.
- **HCD nr. 58** (indicatori de suspiciune) și, dacă e cazul, anexa HCD 74.
- Evaluatorul autorizat = **entitate raportoare** (art. 5).

## 2. Ce generează aplicația (de validat fiecare)
| Document/funcție | Temei invocat în cod | De verificat de jurist |
|---|---|---|
| Norme interne de prevenire | L.129 + Ordin 37/2021 | Conținut minim obligatoriu; adaptare PFA vs PJ |
| Evaluarea de risc a relației | Norme art. 12–13; risc sporit L.129 art. 17 | Factorii de risc, ponderile, pragurile |
| Decizia de desemnare a persoanei responsabile | Norme art. 7 (excepția PFA) | Cine e obligat să desemneze; formă |
| Fișa KYC (PF/PJ + beneficiar real >25%) | L.129 art. 11, 19 | Câmpuri obligatorii, măsuri simplificate/sporite |
| RTN — raport tranzacții în numerar | prag numerar | **Prag corect: 10.000 € vs alt prag?** |
| RTS — raport tranzacții suspecte | L.129 art. 6; HCD 58 | Format ONPCSB, conținut, termen |
| Categorisirea de risc (redus/standard/sporit) | logica internă `risc.py` | Praguri și criterii |
| Indicatori de suspiciune | HCD 58 art. 6(10) | Lista completă și corectă |

## 3. Întrebări deschise (decizie juridică necesară)
1. **Pragul de numerar:** aplicația folosește **10.000 €**. Consiliul de review a semnalat că pentru
   **tranzacții ocazionale** pragul ar putea fi **3.000 €** (L.129 art. 6 alin. 1 lit. b), iar KYC
   simplificat până la 15.000 € (Norme art. 5). **Care e pragul corect pentru un evaluator?**
2. **Screening PEP/sancțiuni:** Normele 37/2021 cer consultarea bazelor de date actuale. Aplicația
   **nu** face screening live (liste demonstrative injectabile). **E suficient ca aplicația să
   trimită evaluatorul către surse oficiale + bifă manuală, sau e obligatorie integrarea unui API?**
3. **Tipping-off (art. 38):** RTS/RTN se păstrează în folderul `aml_confidential` separat de dosar.
   **E acceptabil să se persiste local, sau trebuie generate o singură dată fără urmă pe disc?**
4. **Răspundere (art. 33):** drafturile sunt generate (parțial cu AI). **Ce formulări/disclaimere
   sunt necesare ca evaluatorul să nu fie expus la „neglijență gravă"?**
5. **Norme interne generice vs adaptate:** un model generat e suficient ca **draft**, dar ce trebuie
   neapărat personalizat la entitate înainte de a fi „în vigoare"?
6. **Retenția datelor** (KYC, registre): perioadă, drept de ștergere, registru de prelucrări.

## 4. Livrabil cerut de la jurist
- Confirmarea/corectarea pragurilor și a logicii de risc.
- Validarea (sau rescrierea) șabloanelor de documente.
- Decizia privind screening-ul (API obligatoriu sau nu).
- Lista de disclaimere/formulări obligatorii.
- Confirmarea regulii de păstrare RTS/RTN (tipping-off).

*Fișierele-sursă ale șabloanelor: `src/evaluare/aml/documente.py`, `risc.py`, `indicatori.py`,
`raportare.py`, `liste.py`. Le pot exporta ca `.docx` exemplu la cerere.*
