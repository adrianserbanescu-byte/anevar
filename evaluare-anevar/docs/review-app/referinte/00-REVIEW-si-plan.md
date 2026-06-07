# Review UI nou vs UI vechi — ce s-a pierdut + plan de recuperare

> Audit funcțional (frontend+backend) + a11y, în 4 fluxuri (vezi 1-4 din acest folder). Răspuns la
> observațiile owner-ului + cauză + plan imediat/scurt. **Cauza-rădăcină:** UI-ul nou a fost construit ca o
> coajă „output-first" simplificată; NU s-a portat logica wizardului (câmpuri dinamice, ajutor, descoperire,
> curs, AML/GDPR/Audit, anexe). **TOT backend-ul există** — sunt regresii 100% de frontend. Actualizat: 2026-06-06.

## Răspuns punct-cu-punct la observațiile tale
| # | Observația ta | Verdict | Dovadă |
|---|---------------|---------|--------|
| 1 | „?" șters, doar „!" | **CONFIRMAT** — `wireAjutor()` (wizard.html:703-744) lipsește din dosar.html; e doar „!" (marcat „temporar/dev"). CSS pt ambele există. | 1-paritate |
| 2 | a11y/UX slabe | **CONFIRMAT** — sub-tab-uri fără afordanță, „?" lipsă, ordine titluri ruptă | 4-a11y |
| 3 | sub-tab-uri fără butoane | **CONFIRMAT** — `.subtabs` inactive = fill aproape invizibil + bordură <3:1, `box-shadow:none`; `.tabs` din grila au cadru de folder | 4-a11y |
| 4 | nu mai trage cursul EUR | **CONFIRMAT** — zero `curs-bnr` în dosar.html; `asambleaza()` nu trimite cursul; backend-ul îl folosește încă (meta.py:28) | 1-paritate |
| 5 | flux denumire folder ilogic | **CONFIRMAT** — „Dosar nou" creează cu `wizard:{}` gol → nume `?_?_?`; identitatea se cere prea târziu, fără validare/freeze | 1-paritate |
| 6 | comentariul „Identificare (obligatorii… se blochează…)" | **FALS în cod** — nimic obligatoriu la creare, nimic nu se blochează după generare → text înșelător | 1-paritate |
| 7 | la tip proprietate nu se mai schimbă câmpurile | **CONFIRMAT, CRITIC** — select-ul n-are `onchange`/`aplicaTip`; grupurile (ap-fields/agr-fields/grup-teren/grup-constructie) + câmpurile condiționate (etaj, cotă indiviză, înălțime liberă, categorie folosință, clasă calitate) au DISPĂRUT, deși `BuildingData`/`LandData` le suportă | 1-paritate |
| 8 | sub-tabul Comparabile nu mai cere info de căutare | **CONFIRMAT** — doar textarea + link extern; zero formular de descoperire (județ/localitate/atribute/buton/tabel/bifare) | 2-descoperire |
| 9 | AML/GDPR/Audit = doar redirect | **CONFIRMAT** — tab-urile = doar linkuri; backend 100% gata, de portat formularele in-place | 3-aml |
| 10 | la Generează aveai mai multe opțiuni | **CONFIRMAT** — demo/adnotări/foto/audit pierdute (gated „comercial" / hardcodat) | 1-paritate |
| 13 | audit detaliat nou vs vechi | **LIVRAT** (acest folder) | — |
| 14 | nimic la Anexe; ar trebui sub-tab al Raportului, înainte de Generează | **CONFIRMAT + text FALS** — backend-ul embedează deja foto (Anexa 2)+scanuri (Anexa 3) (`generator._adauga_anexe`); `asambleaza()` omite `photos`/`documente`. Mutarea Anexe între Calcul și Generează = fezabilă, **zero backend** | 3-aml |
| — | „AI TĂIAT modulul de căutare" | **CONFIRMAT** | 2-descoperire |

## Plan de recuperare (toate = frontend; backend gata)
### 🔴 IMEDIAT (azi — fixuri ieftine, mare impact)
1. **Re-adaugă ajutorul „?"** lângă „!" (port `wireAjutor` din _helpers.js/wizard) — ambele popovere.
2. **Sub-tab-uri cu afordanță de buton** (CSS: bordură `--field-border` + emboss; activ = sienna).
3. **Curs EUR/BNR** — re-cablez `/api/curs-bnr` în Calcul + îl trimit în payload.
4. **Comentariul fals „Identificare…"** — reformulez să reflecte realitatea (sau implementez validarea).
5. **Anexe = sub-tab al Raportului, ÎNTRE Calcul și Generează** + upload foto/scanuri → `photos`/`documente` în `asambleaza()` (textul „comercial" e fals).

### 🟠 SCURT (1-3 iterații — recuperarea funcțională grea)
6. **Câmpuri dinamice per tip proprietate** — port `aplicaTip` + grupurile condiționate (cel mai critic gol funcțional).
7. **Modulul de descoperire INLINE în Comparabile** — formular căutare (județ/localitate/atribute) → tabel rezultate → bifare → import în grilă; + import URL/extensie. (reutilizează /api/descopera, /api/import-*).
8. **Grilele reale** (teren/casă/chirii) cu ajustări pe etape + alertele prudențiale 25%/15% (control GEV 520 pierdut acum).
9. **AML / GDPR / Audit in-place** în sub-tab-uri (port formulare din aml.html; +endpoint mic `/api/dosar/{uid}/audit.txt` pt fluxul pe foldere).
10. **Opțiuni Generează** (adnotări/demo) + flux identitate/lock corect (leagă de #5/#6).

## Recomandare strategică
Sub-tab-urile **Proprietate / Comparabile / Calcul** ale UI-ului nou ar trebui să **reutilizeze logica probată a
wizardului** (câmpuri dinamice + descoperire + grile), nu textareas simplificate. Practic: portez markup+JS din
wizard.html/descoperire.html/grila.html în sub-tab-urile dosar.html, păstrând structura „output-first" (tab-urile).
Efort: mediu, dar **fără cod backend nou** — toate API-urile există. Riscul real e doar de UI/JS, acoperit de e2e.
