# Audit User Journey / Cognitive Walkthrough — Evaluare ANEVAR (2026-06-11)

READ-ONLY. Parcurgere pas-cu-pas a întregului drum al unui **evaluator autorizat ANEVAR la prima
utilizare**, de la creare cont până la raport `.docx` generat + dosar AML. Metodă: cognitive
walkthrough — la fiecare pas patru întrebări:
(a) știe userul ce să facă aici? (b) e acțiunea următoare vizibilă/evidentă? (c) înțelege ce s-a
întâmplat după acțiune? (d) unde s-ar bloca / abandona?

Complementar (nu duplicat) cu `docs/audit-ux-2026-06-11.md`, care listează 15 frecușuri pe ecrane.
Aici lentila e **harta de călătorie**: stările, intenția, tranzițiile ÎNTRE pași și **golurile de
orientare** (pași lipsă, salturi bruște, lipsă de „unde sunt / ce urmează").

Cod relevant: `src/evaluare/web/routers/{curent,pagini,aml,descoperire}.py`,
`src/evaluare/web/templates/curent/{cont,incepe,dosar}.html`, `_nav_cross.html`, `aml.html`.

---

## Harta călătoriei (state map)

| # | Stare | Intenția userului | Tranziție / declanșator | Frecuș principal | Risc abandon |
|---|-------|-------------------|--------------------------|------------------|--------------|
| 0 | `/` → redirect | „Deschid aplicația" | auto → `/cont` (fără cont) sau `/incepe` | — | mic |
| 1 | `/cont` (creare cont) | „Mă identific" | „Salvează contul" → `/incepe` | format nume dosar = decizie grea, fără default | mediu |
| 2 | `/incepe` (ÎNCEPE) | „Încep un dosar" | „Dosar nou" → formular inline → `/dosar/{uid}` | 3 butoane egale, niciun „pasul următor" | mediu |
| 3 | Workspace · **Proprietate** | „Descriu proprietatea" | tastare + auto-save | obligatorii nemarcate; mult de completat | mare |
| 4 | Salt → **Comparabile** | „Aduc comparabile" | click sub-tab (gated pe județ+localitate) | gating tăcut + îngheț ireversibil zonă | mare |
| 5 | **Descoperă / grile** | „Caut + ajustez" | Caută → bifează → Importă → grilă → Trimite | lanț lung, 3 „locuri" (rezultate ≠ textarea ≠ grilă) | mare |
| 6 | Salt → **Calcul** | „Văd valoarea" | „Calculează" → valoare + alerte | metoda implicită „cost" greșită pt apartament; eroare 422 târzie | mediu |
| 7 | Salt → **Anexe** | „Atașez foto/scanuri" | upload | ușor de SĂRIT (nu e cerut nicăieri) → raport fără Anexa 2/3 | mediu |
| 8 | Salt → **Generează** | „Produc raportul" | bifează asumare → „Generează" → `.docx` | tab-ul AML/GDPR nu e cerut înainte de generare | mediu |
| 9 | Tab **AML** (alt nivel de tab!) | „Conformitate" | descoperit doar dacă userul vede tab-ul de sus | NU e parte din fluxul Proprietate→Generează | mare |
| 10 | După raport | „Și acum?" | — (descărcare `.docx`, fără „următorul pas") | niciun ghidaj post-generare (PDF? AML? trimit la bancă?) | mediu |

Două axe de tab-uri suprapuse: **tab-ul de sus** (Raport / AML / GDPR / Audit) și **sub-tab-urile
Raport** (Proprietate → Comparabile → Calcul → Anexe → Generează). Fluxul liniar „Înainte ▶" parcurge
DOAR sub-tab-urile Raport; AML/GDPR/Audit rămân în afara drumului ghidat — userul trebuie să le
descopere singur (vezi J-6).

---

## FLUX onboarding (pașii 0–2)

### J-1 (high) — Pasul „format nume dosar" e prima decizie a userului și e cea mai grea, fără default
`templates/curent/cont.html` (fieldset „Format nume dosar", min 3 câmpuri, niciun bifat implicit).
Imediat după nume+legitimație, userul (prima dată) trebuie să aleagă din ~10 checkboxuri ce câmpuri
compun numele FIECĂRUI dosar viitor — o decizie de configurare structurală, irelevantă pentru intenția
lui de moment („vreau să evaluez o casă"). Walkthrough: (a) NU — nu știe ce consecințe are alegerea;
(b) parțial — previzualizarea ajută, dar nu spune „poți schimba mai târziu" (poți, din `/setari`, dar
nu e semnalat aici); (d) se poate bloca pe „ce bifez?". Recomandare: pre-bifează un default sensibil
(`nume_client · tip_proprietate · data_raport`), marchează-l „recomandat", și adaugă „poți modifica
oricând din Setări". Mută complexitatea într-un „avansat" pliabil.

### J-2 (medium) — Tranziția cont → ÎNCEPE nu spune „ce urmează"; cele 3 acțiuni par echivalente
`cont.html` redirect (800ms) → `/incepe`; `curent/incepe.html` (`.actiuni-incepe`: Dosar nou / Încarcă
/ Importă, lățimi egale).
După „✓ Cont salvat" userul aterizează cu 3 butoane de lățime egală. La prima rulare, „Încarcă dosar
salvat" și „Importă dosarul tău" nu au ce procesa (0 dosare), dar arată la fel de proeminente ca
„Dosar nou". (b) acțiunea evidentă NU e evidențiată. Empty-state-ul de mai jos repetă CTA „Dosar nou",
deci mesajul corect EXISTĂ, dar e sub cele 3 butoane confuze. Recomandare: la 0 dosare, „Dosar nou" =
primar, celelalte două estompate/într-un „alte opțiuni"; un rând de bun-venit cu link la
`/documente/ghid-start` (există ghidul, dar nimeni nu trimite userul nou la el din ÎNCEPE).

### J-3 (medium) — Niciun „onboarding tour" sau indicație de progres la primul dosar
`curent/incepe.html` + `curent/dosar.html`.
Userul nou trece din ÎNCEPE direct în workspace-ul cu 2 axe de tab-uri și ~40 de câmpuri, fără niciun
fir („Pas 1 din 5: descrie proprietatea"). Ghidul (`/documente/ghid-start`, 6 pași) e excelent, dar
ascuns în nav-ul „Ajutor" și nedeschis automat. (a)/(d): primul contact cu workspace-ul = supraîncărcare
cognitivă, punct clasic de abandon. Recomandare: la PRIMUL dosar (0 dosare anterioare), afișează un
banner subtil „Nou aici? Vezi ghidul în 6 pași" + opțional evidențiază sub-tab-ul curent ca „pasul 1/5".

---

## FLUX workspace — Proprietate → Comparabile → Calcul → Anexe → Generează (pașii 3–8)

### J-4 (high) — Saltul Proprietate → Comparabile e „gated" tăcut; userul nu înțelege ce s-a întâmplat
`curent/dosar.html` funcția `paznic`/`poateIntra` + `#gate-descopera`.
La click pe sub-tabul „Comparabile" fără județ+localitate, switch-ul e blocat prin
`stopImmediatePropagation`, apare un avert sus și focusul sare pe `#judet` (alt sub-tab, posibil
nevizibil). Walkthrough: (c) userul NU înțelege ce s-a întâmplat — a dat click pe un tab care „nu face
nimic"; (b) nu e evident că tab-ul e blocat (arată ca un tab normal, fără lock/`aria-disabled`). Punct
de confuzie major: „de ce nu merge?". Recomandare (convergent cu F2-1): marchează vizual sub-tabul ca
blocat (iconiță lock + `aria-disabled="true"`) și pune motivul ÎN tab/lângă el, nu doar într-un banner
sus pe care userul nu-l corelează cu click-ul.

### J-5 (high) — Înghețarea ireversibilă județ/localitate se produce la prima intrare în Comparabile, fără avertizare prealabilă
`curent/dosar.html` `inghetZona()` (la primul switch valid → `disabled` peste tot, fără confirm).
Userul care, abia, a completat județ+localitate ca să intre în Comparabile, fixează DEFINITIV zona
fără să știe — corectarea unei greșeli (județ ales greșit) cere apoi „dosar nou" (clonare). (c)/(d):
consecință mare, ascunsă; userul descoperă blocajul abia când vrea să corecteze. Recomandare
(convergent cu F2-2): confirm explicit la primul switch („Județul și localitatea se fixează acum și nu
mai pot fi schimbate în acest dosar") SAU oferă o cale de corecție tipografică ca la identitate
(`Deblochează`), nu doar clonare integrală.

### J-6 (high) — Modulul AML e în AFARA drumului ghidat; userul îl poate rata complet → neconformitate Legea 129
`curent/dosar.html`: tab AML e pe axa de sus (Raport/AML/GDPR/Audit); fluxul „Înainte ▶"
(`SUBTABS`) parcurge DOAR Proprietate→Comparabile→Calcul→Anexe→Generează.
Întrebarea din brief — „cum ajunge userul la AML?" — are răspuns problematic: **nu ajunge prin flux**.
Nimic nu îl conduce de la Generează la AML; bara „Înainte ▶" nu trece niciodată prin AML; nu există
niciun gating care să spună „pentru garantare credit ai obligații AML". Un evaluator concentrat pe
raport poate genera `.docx`-ul și pleca FĂRĂ dosar AML — exact obligația legală pe care app-ul vrea să
o asiste (Legea 129/2019). Walkthrough: (a) NU știe că trebuie; (b) AML e vizibil ca tab dar fără
„chemare"; (d) abandon silențios al unei obligații legale. Recomandare: la scop=`garantare`, adaugă
pe Generează (sau ca pas în „Înainte") un prompt/checklist „Conformitate AML necompletată — pentru
garantare e obligatorie. Mergi la AML" + un indicator de stare AML (necompletat/evaluat) lângă tab.

### J-7 (medium) — Tab-ul Anexe e ușor de sărit; raportul iese fără foto/scanuri (Anexa 2/3) fără avertizare
`curent/dosar.html` sub-tab Anexe + Generează; `genereaza` nu verifică prezența anexelor.
Anexele (foto = Anexa 2, scanuri = Anexa 3) sunt „opționale" tehnic, dar SEV 2025/GEV 630 le cere.
Userul care merge Calcul → Generează (sărind Anexe via „Continuă la Generează →" din rezultatul
calculului, care duce direct la `s-genereaza`) produce un raport fără anexe, fără niciun semnal. (b)/(c):
nimic nu amintește. Recomandare: la generare fără anexe + scop=garantare, un confirm soft („Raportul nu
are fotografii/scanuri — cerute de SEV 2025. Continui?"); sau un indicator „Anexe: 0 foto / 0 scanuri"
pe Generează.

### J-8 (medium) — „Continuă la Generează →" sare peste Anexe; tranziție bruscă Calcul→Generează
`curent/dosar.html` butonul `#la-gen` (din rezultatul `/calcul`) → `subtab("s-genereaza")`.
După un calcul reușit, singurul CTA propus duce DIRECT la Generează, sărind Anexe. Userul urmează firul
oferit și ratează un pas de conformitate. (b): firul ghidat e incomplet. Recomandare: CTA-ul să ducă la
„Anexe" (pasul cronologic următor) sau să ofere ambele („Adaugă anexe" / „Generează direct").

### J-9 (medium) — Metoda de calcul implicită („cost") e greșită pentru apartament/teren; eroare descoperită târziu
`curent/dosar.html` `<select id="metoda">` default `cost`; `aplicaTip()` dezactivează cost/ponderată
pt apartament/agricol și comută pe „piata", dar userul ajunge la Calcul cu set de date incomplet.
Pentru un apartament, abordarea prin cost nu se aplică; `aplicaTip` ascunde câmpurile de cost și mută
metoda, dar dacă userul n-a completat comparabile, „Calculează" întoarce 422. (a)/(c): userul nu știe
de ce metoda s-a schimbat singură, nici de ce calculul cere comparabile. Recomandare: pe sub-tabul
Calcul, o linie contextuală „Pentru {tip} se folosește abordarea prin {metodă}; ai nevoie de {N}
comparabile" — leagă metoda de tipul ales și de ce date lipsesc.

### J-10 (medium) — Câmpurile obligatorii pentru calcul nu sunt marcate; userul descoperă lipsa abia la „Calculează" (422)
`curent/dosar.html` tab Proprietate (suprafețe, comparabile) — niciun marcaj „obligatoriu".
Inconsistent cu pagina Cont (care are `required`+`aria-required`+erori inline). Userul completează ce
crede, apasă Calculează, primește un 422 (acum formatat citibil — bun) DAR pe alt sub-tab decât cel cu
câmpul lipsă. (b)/(d): efort risipit, frustrare. Recomandare (convergent F1-3): marchează vizual minimul
necesar pe Proprietate/Comparabile; validare la blur, nu doar la submit.

---

## FLUX post-raport (pașii 9–10)

### J-11 (high) — După „Generează" nu există niciun „ce urmează"; călătoria se termină brusc
`curent/dosar.html` `genereazaRaport()` → mesaj „✓ raport.docx generat ... salvează-l ca PDF local".
Întrebarea din brief — „ce face userul după ce a generat raportul?" — nu are răspuns în UI. Mesajul de
succes spune doar „salvează-l ca PDF local". Nimic despre: ai făcut AML? trebuie să-l trimiți la bancă?
trebuie să încarci raportul submis înapoi (ADR-003)? E starea de „și acum?" clasică. (c)/(d): userul
nu știe dacă a TERMINAT. Recomandare: după generare, un panou „Pașii finali": (1) verifică `.docx` +
salvează ca PDF; (2) completează/verifică AML (dacă garantare și necompletat); (3) după trimitere,
încarcă raportul submis pentru amprentă de integritate. Transformă finalul în checklist, nu în dead-end.

### J-12 (high) — Manualul descrie un selector de format (PDF/.zip) care NU mai există în UI → așteptare înșelată
`docs/manual-utilizare.md` §4.5 pct.3 („Alegi formatul ... Word / PDF / Amândouă (.zip)") vs
`curent/dosar.html` care are DOAR butonul „Generează și descarcă raportul (.docx)" + hint „salvează ca
PDF manual"; `routers/curent.py:genereaza` confirmă: „App-ul NU mai produce PDF (decizie 2026-06-08)".
Userul care a citit ghidul caută un selector de format inexistent → confuzie „unde aleg PDF?". (a)/(c):
documentația și produsul s-au decuplat. Recomandare: actualizează `manual-utilizare.md` §4.5 (și
ghidul `ghid/05-raport` dacă spune la fel) la realitatea „doar .docx, PDF manual". (Findingul vizează
documentația ca parte a journey-ului, nu codul.)

### J-13 (medium) — Pagina AML standalone `/aml` are dată hardcodată învechită (`2026-06-03`) și e accesibilă deși nelinkată
`templates/aml.html` L48 `<input ... id="azi" value="2026-06-03">`; `routers/aml.py:128` rută vie `/aml`.
Userul care nimerește `/aml` (URL salvat, link extern, istorie) lucrează pe o pagină PARALELĂ
necorelată cu dosarul, cu data fixată în trecut — documente AML generate cu dată greșită (relevant
juridic: RTS „de îndată", RTN termen 3 zile). (c)/(d): două surse AML, una cu bug de dată. Recomandare
(convergent F3-1/F3-2): redirect `/aml` → workspace-ul dosarului activ sau scoate ruta; dacă rămâne,
default data = azi.

### J-14 (medium) — Tab AML cere re-introducerea unor date deja completate pe Proprietate (client, dată)
`curent/dosar.html` tab AML: pre-completează DOAR `aml_nume` din `nume_client` și `aml_azi` din
`data_evaluarii`; restul (prenume, CNP, tip client PF/PJ) se reintroduc.
Userul a declarat deja clientul pe Proprietate; pe AML reîncepe parțial. (a)/(d): senzație de muncă
dublă, descurajează completarea AML (deja opțională în flux — vezi J-6). Recomandare: propagă tot ce se
poate din identitatea dosarului (nume/prenume split din `nume_client`, tip client din `tip_proprietate`
client PF/PJ unde se poate deduce), lasă userul doar să confirme/completeze.

### J-15 (medium) — „Dosare dispărute" (folder șters) e o stare de eroare în care userul aterizează fără cale clară de revenire
`curent/incepe.html` secțiunea `diff.disparute` + `/api/dosar/{uid}/scoate-din-index`.
La revenirea în ÎNCEPE, un dosar al cărui folder a fost mutat/șters din afara app-ului apare ca
„dispărut" cu doar „scoate din listă". Userul nu știe dacă datele-s pierdute sau recuperabile. (c)/(d):
panică „mi-am pierdut dosarul?". Recomandare (convergent F4-2): o linie „Folderul a fost mutat/șters din
afara aplicației; dacă l-ai mutat, readu-l în `date/dosare/`, altfel scoate-l".

### J-16 (low) — `/dosare` legacy = dead-end pe traseul „dosarele mele"
`templates/dosare.html` + `routers/pagini.py:/dosare` (butonul „Deschide" nu deschide; nav duce la
`/incepe` ca „Toate dosarele").
Userul care ajunge pe `/dosare` (URL vechi) lovește un perete. (b)/(d): două liste, una moartă.
Recomandare (convergent F1-1/F4-1): redirect `/dosare` → `/incepe#salvate` sau scoate ruta din build.

### J-17 (low) — Acțiuni globale (Backup TOATE dosarele, Documente) sunt în bara de jos a UNUI dosar
`curent/dosar.html` `.btn-bar-jos` (Backup dosare / Documente).
Userul nu caută acțiuni la nivel de aplicație în footer-ul unui dosar individual. (b): loc neașteptat.
Recomandare (convergent F1-6): mută Backup pe ÎNCEPE/Setări.

---

## Goluri de drum (tranziții / orientare) — sinteză

1. **Două axe de tab-uri necoordonate**: fluxul liniar „Înainte ▶" acoperă doar sub-tab-urile Raport;
   AML/GDPR/Audit sunt insule. Cel mai grav: **AML nu e niciodată „chemat"** pe traseu (J-6) deși e
   obligația legală centrală la garantare.
2. **Tranziții care sar pași**: „Continuă la Generează →" sare Anexe (J-8); raportul poate ieși fără
   anexe (J-7) și fără AML (J-6), fără niciun semnal.
3. **Decizii ireversibile fără avertizare prealabilă**: îngheț zonă (J-5), identitate asumată.
4. **Lipsă de „unde sunt / ce urmează"**: niciun indicator de progres dosar (Proprietate ✓ ·
   Comparabile 3 · Calcul — · AML —); onboarding-ul nu deschide ghidul (J-3); finalul e dead-end (J-11).
5. **Documentație decuplată de produs**: manualul promite un selector de format PDF inexistent (J-12).

---

## Recomandare-cheie (un singur fir)

Adaugă un **indicator de progres al dosarului** vizibil permanent (chips: Proprietate · Comparabile ·
Calcul · Anexe · AML · Raport, cu stare ✓/—) și fă fluxul „Înainte ▶" să includă AML ca pas
condiționat de scop. Asta rezolvă simultan J-3, J-6, J-7, J-8 și J-11 — adică toate golurile de
orientare și de tranziție dintr-o singură intervenție de UX.
