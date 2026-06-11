# Audit euristic UX (Nielsen, 10 euristici) — App evaluare ANEVAR

Data: 2026-06-11 · Mod: READ-ONLY · Persona: evaluator autorizat ANEVAR
Scop app: evaluare imobiliară casă+teren pentru garantare credit bancar (SEV 2025, GEV 520/630).

Domeniu analizat: flux complet cont → /incepe → workspace /dosar/{uid}
(taburi Proprietate / Comparabile / Calcul / Anexe / Generează + AML / GDPR / Audit),
plus pagini standalone /grila, /descoperire, /aml și navigația globală (_nav_cross).

Fișiere-cheie inspectate:
- `src/evaluare/web/templates/curent/dosar.html` (workspace, 1518 linii)
- `src/evaluare/web/templates/curent/incepe.html`, `cont.html`, `setari.html`
- `src/evaluare/web/templates/_nav_cross.html`, `_cartus.html`, `_feedback.html`, `_design.css`
- `src/evaluare/web/templates/grila.html`, `descoperire.html`, `aml.html`
- `src/evaluare/web/routers/curent.py`, `pagini.py`

Legenda severitate: critical / high / medium / low.

---

## H1 — Vizibilitatea stării sistemului

**[medium] Indicatorul de salvare nu confirmă persistența reală pe disc.**
`dosar.html:703-707` — `salveaza()` afișează „● salvat în folder" imediat ce `fetch` întoarce
`r.ok`, dar autosave-ul e debounce 700ms și un `beforeunload`/închidere de tab în fereastra de
debounce pierde ultimele modificări fără niciun avertisment. La un document semnabil de garantare,
„salvat" trebuie să însemne salvat. Fix: flush la `beforeunload` (sendBeacon există deja pentru
unlock — refolosește pattern-ul) + nu marca „salvat" cât timp `tSave` e pending.

**[low] Inconsistență de copy pe același indicator de salvare.** La încărcare scrie „salvat
**automat** în folder" (`:64`), după prima salvare scrie „salvat în folder" (`:705`). Două
formulări pentru aceeași stare — aliniază la un singur text.

**[low] Lipsă feedback de progres la operațiile lungi de descoperire.** `dosar.html:1086` /
`descoperire` — scraping-ul pe 2 portaluri × N localități poate dura zeci de secunde; userul vede
doar „… se caută" static, fără spinner, fără „portal 1/2", fără posibilitate de anulare. Pe conexiuni
lente pare „blocat". `_design.css` are deja `.spinner` + `[aria-busy]` — neutilizate aici.

---

## H2 — Potrivirea sistem ↔ lume reală

**[medium] Jargon intern de dezvoltare expus userului final.** Workspace-ul conține encoding-uri
care nu înseamnă nimic pentru un evaluator: `CIN`/`CIB` (`dosar.html:557,559`), `VBP`
(`:342,364,1404`), titluri de fieldset „Date de cost (abordarea prin cost)", referințe „ADR-003"
în titlurile de tooltip vizibile (`:505` „read-only (ADR-003)"), „GEV 630" pe un titlu de fieldset
de utilități (`:227`). Codurile metodologice (GEV 520/630, SEV) sunt corecte ca trasabilitate, dar
„ADR-003" e cod intern de arhitectură — nu trebuie să apară în UI. Fix: scoate „ADR-003" din texte
vizibile; expandă acronimele la prima apariție (ex. „VBP (venit brut potențial)").

**[low] „Urmă de audit (.txt)" / „snapshot" / „hash" în limbaj tehnic.** Tabul Audit
(`:489`) și butoanele asociate folosesc „jurnal hash-înlănțuit", „validare încrucișată" — corect
tehnic, dar un evaluator beneficiază de o frază introductivă în limbaj de business („dovada că
valorile din raport corespund cu datele introduse").

**[low] Placeholder-e cu format crud expus.** Ex. `comparabile` placeholder `250000;120`,
`depreciere` `5;0.05`, `elemente` `Structura;X;mp;120;2000;2015` (`:249,252,309`). Deși grila
editabilă (`gridEditabil`) acoperă acum aceste textarea, placeholder-ul „;"-delimited rămâne
vizibil în câmpul `comparabile_teren`/`incalzire` etc. și sugerează sintaxă manuală.

---

## H3 — Control și libertate (undo / anulare / ieșire)

**[high] „Reset dosar" golește TOT formularul fără undo și fără a salva o copie.**
`dosar.html:1511-1515` — un singur `confirm()` apoi se șterg toate input/textarea/select. Nu există
undo, nu se face snapshot înainte. Pe un dosar cu zeci de câmpuri + grile completate, o atingere
greșită = pierdere de muncă. Confirm-ul spune chiar „folderul rămâne pe disc; salvează după" — adică
ultima versiune NU e auto-protejată. Fix: salvează automat o versiune înainte de reset (folderul are
deja versionare .docx — extinde la wizard) sau oferă „Anulează reset" (restore din snapshot în memorie).

**[medium] Ștergerea dosarului nu e accesibilă din workspace și nu există coș/undo.** Endpoint
`/api/dosar/{uid}/sterge` (`curent.py:166`) e definitiv, dar din UI ștergerea unui dosar din listă nu
apare deloc în `/incepe` (doar „scoate din listă" pentru dosare dispărute). Userul nu poate șterge
ordonat un dosar greșit creat — sau, dacă o face altundeva, e ireversibil. Fix: acțiune explicită de
ștergere cu pas de confirmare dublu + perioadă de recuperare.

**[medium] Imposibil de schimbat scopul/tipul după creare, fără ieșire clară.** `dosar.html:573-575`
— `tip_proprietate` și `scop` devin `disabled` cu title „creează un dosar nou". Corect ca regulă de
identitate, dar dacă userul a greșit tipul la creare, singura cale e să re-creeze tot dosarul manual
(nu există „clonează cu alt tip"). Clonarea (`:518`) păstrează identitatea read-only doar pe dosare
asumate, nu acoperă cazul „am ales greșit casa în loc de apartament la pasul de creare".

---

## H4 — Consistență și standarde

**[high] Două navigații cu modele mentale diferite pe aceeași aplicație.** `_nav_cross.html`
(folosit de UI-ul „curent") listează „Toate dosarele / Grile / Flux livrabile / Documente / Setări /
Ajutor", în timp ce paginile vechi (`grila.html:20`, `aml.html:25`) folosesc `_topbar.html` și au
propriul buton „◀ Înapoi la dosar" plasat în corp (`grila.html:27`), nu în bară. `/grila` și
`/descoperire` se deschid în tab nou din workspace (`dosar.html:346`) — userul aterizează pe o pagină
cu altă structură de nav decât cea din care a plecat. Coexistă efectiv 2 sisteme UI (vezi și
`/wizard`, `/formular`, `/dosare`, `/alege` încă rutate în `pagini.py:115-132`). Fix: o singură bară
de navigație + un singur model de „înapoi".

**[medium] Buton „brand" cu funcție de „înapoi" — etichetare inconsistentă.** Pe workspace topbar-ul
brand spune „← Dosarele mele" (`dosar.html:59`), iar pe celelalte pagini brand-ul spune „Evaluare
ANEVAR" (`incepe.html:22`, `cont.html:10`). Același element vizual (`.brand`) are uneori rol de logo,
alteori rol de buton-înapoi — userul nu poate prezice comportamentul.

**[medium] Terminologie variabilă pentru aceeași entitate.** „Dosarele mele" (topbar workspace) vs
„Toate dosarele" (nav) vs „Dosare salvate" (titlu `/incepe`) vs „ÎNCEPE" (cartuș `/incepe`) descriu
aceeași destinație/pagină. Trei nume diferite pentru lista de dosare cresc sarcina cognitivă.

**[low] Stil de „callout/avert" mixt inline vs clasă.** Multe avertismente folosesc `class="avert-warn"`
dar cu `style="..."` inline (`dosar.html:107`), altele clasa pură. Întreținere fragilă + risc de
deviere vizuală.

---

## H5 — Prevenirea erorilor

**[high] „Continuă la Generează" după calcul nu garantează că raportul se va genera.**
Calculul (`/calcul`) e advisory pe blocaje de date (200 + alertă), DAR generarea raportului
(`curent.py:276-282`) e fail-closed și ridică 422 pe aceleași probleme blocante. Userul vede „Valoare:
X" + butonul „Continuă la Generează →" (`dosar.html:1459`), bifează asumarea, apasă Generează — și
abia atunci primește respingerea. Calea fericită îl duce într-un zid. Fix: dacă există alerte
`nivel="blocheaza"` la calcul, dezactivează/avertizează butonul „Continuă la Generează" cu motivul,
nu lăsa userul să descopere blocajul după checkpoint-ul de asumare.

**[medium] Validarea câmpurilor numerice e tăcută până la submit.** Suprafețe, prețuri, ani,
fracții de depreciere — niciun câmp nu e validat la blur. Un „acd" gol sau „au > acd" se descoperă
doar ca eroare 422 după Calculează (`dosar.html:1462`). Pentru câmpuri cu regulă cunoscută (Au ≤ Acd,
fracție 0–1, an ≤ azi) validarea inline previne eroarea înainte să apară.

**[medium] Datele fără separator clar între „obligatoriu" și „opțional".** Pe Proprietate, multe
câmpuri sunt opționale (sarcini, acces, observații) iar altele esențiale pentru calcul (acd,
suprafață teren, comparabile), dar UI-ul nu marchează nicăieri ce e strict necesar pentru a ajunge la
o valoare. Userul completează „pe ghicite" și află ce lipsește abia la eroarea de calcul.

**[low] Curs valutar — câmp text liber cu virgulă/punct.** `dosar.html:357,1218` acceptă „4,9750",
îl normalizează la „.". Bine gestionat, dar un user poate tasta format invalid fără feedback până la
calcul. Un `inputmode="decimal"` + validare ușoară ar ajuta.

---

## H6 — Recunoaștere vs reamintire

**[medium] Format dosar setat „o dată" trebuie reamintit, nu e vizibil la crearea dosarului.**
La `/cont` userul alege câmpurile numelui de dosar; la `/incepe` (`incepe.html:47-67`) formularul de
creare cere exact acele câmpuri, dar regula „needitabil ulterior" + „ID client free-text" e îngropată
în hint. Userul nu vede consecințele alegerii (ce devine read-only) decât după ce intră în workspace.

**[medium] Sintaxa grilelor / costurilor depinde de memorarea ordinii coloanelor.** Deși
`gridEditabil` a transformat textarea-urile „;" în tabele cu header (bun), câmpurile rămase libere
(ex. `incalzire` placeholder „centrala_gaz", `d-secundare` „una pe linie") cer userului să-și
amintească valori-cod acceptate, în loc să le aleagă dintr-o listă.

**[low] „Localități vecine" cere tastare liberă de nume corecte.** `dosar.html:270` —
input free-text „Băicoi, Blejoi" pentru extinderea căutării, când restul localităților vin din
dropdown cu slug-uri. Inconsistent: aici userul trebuie să-și amintească/scrie corect numele, riscând
slug-uri ne-potrivite la backend.

---

## H7 — Flexibilitate și eficiență

**[medium] Fără scurtături de tastatură pentru acțiunile frecvente.** Calculează, Generează,
salvare, navigare între sub-taburi — toate doar cu mouse. Un evaluator care procesează multe dosare
ar beneficia de Ctrl+S (forțează salvare), Ctrl+Enter (calculează). Taburile au navigare ARIA cu
săgeți (bun), dar acțiunile nu.

**[low] Valori implicite utile lipsesc la câmpuri previzibile.** `data_raportului` /
`data_evaluarii` / `data_inspectiei` pornesc goale; calculul cade pe „azi" tăcut (`:1208`), iar
generarea cere confirmare (`:1467`). O valoare implicită „azi" (editabilă) la `data_raportului` ar
elimina un confirm recurent. La fel `an_referinta` (placeholder 2025, dar gol).

**[low] Re-căutare comparabile fără memorarea ultimelor filtre.** Filtrele de descoperire (an,
stare, finisaj, teren) nu se persistă între căutări/sesiuni; userul re-completează la fiecare dosar
similar.

---

## H8 — Design estetic și minimalist

**[medium] Tabul Proprietate este foarte dens — multe câmpuri opționale concurează cu cele esențiale.**
Identificare (5 fieldset-uri) + Date fizice (teren, utilități, construcție, cost) pe un singur
sub-tab. Regruparea recentă în fieldset-uri cu titlu (`:118-254`) ajută, dar câmpuri rar folosite
(sarcini, restricții urbanism, observații inspecție, însoțitor) au aceeași greutate vizuală ca acd /
suprafață. Fix: colapsează secțiunile opționale (`<details>`) implicit închise, lasă vizibil setul
minim necesar valorii.

**[low] Popovere „?" injectate pe multe label-uri.** Deși s-au redus (R2, `:649-691`), încă există
~17 chei de ajutor; pe câmpuri al căror label e deja clar (metoda, monedă) tooltipul „?" e zgomot.

---

## H9 — Ajută userii să recunoască/recupereze din erori

**[high] Mesaje de eroare generice pe căi importante.** Multe `catch` afișează texte vagi care nu
spun ce să corecteze:
- Grilă casă: „Grila a eșuat — verifică valorile" (`dosar.html:1299`)
- Descoperire: „Portalul nu a răspuns sau conexiunea a eșuat" (`:1092`)
- AML: „Evaluarea a eșuat — verifică datele" (`:1196`)
- Audit: „generarea a eșuat — verifică valorile" (`:1153`)
Spre deosebire de calcul/raport (care propagă `detail` din 422 — corect, `:1451,1474`), aceste căi
înghit `r.json().detail` și arată un text fix. Userul nu știe CARE valoare e greșită. Fix: propagă
mesajul de eroare din backend peste tot (pattern-ul există deja la `/calcul`).

**[medium] Eșecul listei de localități degradează tăcut într-o stare confuză.** `dosar.html:628-639`
— dacă `/api/localitati` eșuează, dropdown-urile devin opțiune unică cu valoarea salvată și se scrie
un mesaj în indicatorul de SALVARE („⚠ Lista de localități indisponibilă"). Userul vede un avertisment
de „salvare" deși problema e altă cauză (rețea/listă), iar nu poate alege altă localitate. Mesajul e
plasat pe canalul greșit (save-ind), deci se pierde.

**[low] „Niciun comparabil" oferă o singură sugestie.** `dosar.html:1029` — mesaj de stare gol util,
dar fără diferențiere între „0 rezultate reale" și „toate portalurile au eșuat" în textul afișat
userului în lista de rezultate (distincția e făcută doar în statusul scurt de sus).

---

## H10 — Ajutor și documentație

**[medium] Lipsă onboarding la prima utilizare a workspace-ului.** Prima dată când userul intră în
`/dosar/{uid}`, nu există tur/ghid contextual care să explice fluxul Proprietate → Comparabile →
Calcul → Generează. Gating-ul „completează județ+localitatea" (`:89`) apare doar reactiv, la click pe
Comparabile. Există „Ajutor" în nav (`/documente/ghid-start`) și „Flux livrabile", dar nimic
in-context la primul dosar.

**[low] „Ajutor" trimite la un document, nu la ajutor contextual pe ecranul curent.** Link-ul
`/documente/ghid-start` (`_nav_cross.html:13`) deschide documentația generală; nu există „ajutor
pentru ecranul ăsta" (ex. ce face exact „abordarea prin cost" pe tabul Calcul).

**[low] Erorile 404 trimit la rute tehnice.** `pagini.py:110` returnează „Vezi lista completă la
/documente" — corect, dar mesajul expune calea brută în loc de un link.

---

## Sinteză prioritizare

Critical: niciunul (aplicația e funcțională, fără capcane care blochează complet userul).

High (de rezolvat primele):
1. H5 — butonul „Continuă la Generează" promite o cale care e blocată fail-closed la generare.
2. H9 — mesaje de eroare generice pe grilă/descoperire/AML/audit (propagă `detail` peste tot).
3. H3 — „Reset dosar" fără undo / fără snapshot de siguranță.
4. H4 — două sisteme de navigație / „înapoi" inconsistente între UI nou și pagini vechi.

Medium: H1 (salvare ne-garantată la închidere), H2 (jargon ADR-003/CIN/VBP în UI), H6
(format dosar reamintit), H8 (densitate tab Proprietate), H10 (onboarding lipsă).

Low: copy inconsistent salvare, popovere „?", valori implicite, scurtături tastatură.
