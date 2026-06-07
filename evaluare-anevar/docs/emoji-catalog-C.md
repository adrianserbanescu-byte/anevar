# Catalog emoji — paginile C (pentru rollout emoji→SVG)

> Prep pentru PCT 1 (A construiește `_icon.html`, C aplică per-pagină după aprobare).
> Exclus: `dosar.html` (lane A). Generat automat — NU s-a schimbat nimic.

**Total: 119 apariții.** Iconuri-UI (candidate SVG): 78 · glife-text (rămân copy tipografic): 41

## A. ICONURI-UI — candidate SVG (în butoane/linkuri, deja aria-hidden)
| rol icon | nr | locații |
|---|---|---|
| `check` | 12 | _feedback.html:163, _feedback.html:164, cont.html:69, descoperire.html:493, flux_livrabile.html:25, flux_livrabile.html:215, grila.html:175, grila.html:265, grila.html:300, grila.html:330, wizard.html:607, wizard.html:755 |
| `doc` | 7 | _nav_cross.html:7, aml.html:89, aml.html:90, index.html:35, result.html:33, wizard.html:362, wizard.html:377 |
| `warn` | 7 | aml.html:20, incepe.html:85, descoperire.html:75, descoperire.html:301, grila.html:308, wizard.html:266, wizard.html:683 |
| `add` | 7 | incepe.html:21, incepe.html:80, flux_livrabile.html:130, flux_livrabile.html:164, grila.html:256, grila.html:262, grila.html:318 |
| `map` | 4 | _nav_cross.html:6, descoperire.html:401, grila.html:253, index.html:13 |
| `import` | 4 | incepe.html:23, incepe.html:142, incepe.html:151, descoperire.html:81 |
| `edit` | 3 | _feedback.html:15, dosare.html:32, feedback_list.html:15 |
| `delete` | 3 | descoperire.html:86, descoperire.html:171, dosare.html:34 |
| `view` | 3 | descoperire.html:172, descoperire.html:322, wizard.html:374 |
| `refresh` | 3 | grila.html:16, wizard.html:336, wizard.html:337 |
| `folder-open` | 2 | incepe.html:22, dosare.html:14 |
| `arrow-send` | 2 | descoperire.html:85, descoperire.html:411 |
| `download` | 2 | dosare.html:33, feedback_list.html:12 |
| `doc-edit` | 2 | result.html:34, wizard.html:363 |
| `close` | 1 | _feedback.html:22 |
| `thumb-up` | 1 | _feedback.html:28 |
| `thumb-down` | 1 | _feedback.html:29 |
| `swap` | 1 | _nav_cross.html:3 |
| `help` | 1 | _nav_cross.html:8 |
| `import-similar` | 1 | incepe.html:28 |
| `demo` | 1 | incepe.html:29 |
| `folder` | 1 | incepe.html:77 |
| `calendar` | 1 | incepe.html:128 |
| `search` | 1 | descoperire.html:139 |
| `flag` | 1 | grila.html:299 |
| `compass-wizard` | 1 | index.html:27 |
| `check-filled` | 1 | wizard.html:266 |
| `audit-receipt` | 1 | wizard.html:364 |
| `back` | 1 | wizard.html:373 |
| `save` | 1 | wizard.html:376 |
| `block` | 1 | wizard.html:683 |

## B. GLIFE-TEXT — săgeți/buline în COPY (recomand: NU converti, rămân text)
| glyph | nr | locații |
|---|---|---|
| `arrow-right` | 30 | aml.html:121, descoperire.html:76, descoperire.html:83, descoperire.html:232, dosare.html:17, feedback_list.html:18, flux_livrabile.html:130, flux_livrabile.html:155 … |
| `arrow-ext` | 3 | dosare.html:31, grila.html:259, wizard.html:505 |
| `arrow-up` | 2 | descoperire.html:142, descoperire.html:405 |
| `arrow-left` | 2 | document.html:11, result.html:7 |
| `neutral-minus` | 2 | wizard.html:266, wizard.html:516 |
| `bullet` | 1 | descoperire.html:25 |
| `arrow-bi` | 1 | wizard.html:335 |

## C. Detaliu per fișier (fișier:linie · rol · context)

### _feedback.html
- L15 `✎` [edit/icon] — «-hidden="true">§</span> Feedback»
- L22 `✕` [close/icon] — «abel="Închide">§</button>»
- L28 `👍` [thumb-up/icon] — «umb" data-val="§ merge">§ Merge</button>»
- L29 `👎` [thumb-down/icon] — «umb" data-val="§ problemă">§ Problemă</button>»
- L163 `✓` [check/icon] — «ction(){ gata("§ Mulțumim! Feedback salvat."); }»
- L164 `✓` [check/icon] — «ction(){ gata("§ Mulțumim! (salvare locală indis»

### _nav_cross.html
- L3 `⇄` [swap/icon] — «<a href="/">§ Alege interfața</a>»
- L6 `🗺` [map/icon] — «lux-livrabile">§ Flux livrabile</a>»
- L7 `📄` [doc/icon] — «f="/documente">§ Documente</a>»
- L8 `❓` [help/icon] — «te/ghid-start">§ Ajutor</a>»

### aml.html
- L20 `⚠` [warn/icon] — «-hidden="true">§️</span> Aplicația <b>NU verific»
- L89 `📄` [doc/icon] — «-hidden="true">§</span> Politică de prelucrare</»
- L90 `📄` [doc/icon] — «-hidden="true">§</span> Acord consimțământ clien»
- L121 `→` [arrow-right/glyph] — «icatori activi § ${d.propune_rts?'<b class="warn»

### curent\cont.html
- L69 `✓` [check/icon] — «).textContent='§ Cont salvat. Se deschide ÎNCEPE»

### curent\incepe.html
- L21 `➕` [add/icon] — «-hidden="true">§</span> Dosar nou</button>»
- L22 `📂` [folder-open/icon] — «-hidden="true">§</span> Încarcă dosar salvat</a>»
- L23 `📥` [import/icon] — «-hidden="true">§</span> Importă dosarul tău</but»
- L28 `🔁` [import-similar/icon] — «-hidden="true">§</span> Import asemănător <span »
- L29 `🧪` [demo/icon] — «-hidden="true">§</span> Demo <span class="badge »
- L77 `🗂` [folder/icon] — «-hidden="true">§</span>»
- L80 `➕` [add/icon] — «nou').click()">§ Dosar nou</button>»
- L85 `⚠` [warn/icon] — «-hidden="true">§</span> Dosare dispărute (folder»
- L128 `📅` [calendar/icon] — «t = d.value ? '§ '+roData(d.value) : ''; }»
- L142 `📥` [import/icon] — «n.textContent='§ Se importă…'; impStatus.textCon»
- L151 `📥` [import/icon] — «-hidden="true">§</span> Importă dosarul tău';»

### descoperire.html
- L25 `●` [bullet/css] — «fore{ content:"§"; margin-right:4px; }»
- L75 `⚠` [warn/icon] — «-hidden="true">§️</span> Prețurile extrase sunt »
- L76 `→` [arrow-right/glyph] — «ajustare ofertă§tranzacție (tipic −5% … −15%) sa»
- L81 `📥` [import/icon] — «-hidden="true">§</span> Anunțuri importate din e»
- L83 `→` [arrow-right/glyph] — «<b>Import § Evaluare ANEVAR</b>. Prețuri din»
- L85 `➜` [arrow-send/icon] — «-hidden="true">§</span> Trimite bifatele la gril»
- L86 `🗑` [delete/icon] — «-hidden="true">§</span> Golește coada</button>»
- L139 `🔍` [search/icon] — «-hidden="true">§</span>»
- L142 `↑` [arrow-up/glyph] — «ază criteriile §</button>»
- L171 `🗑` [delete/icon] — «-hidden="true">§</span></button></h3>»
- L172 `▶` [view/icon] — «-hidden="true">§</span> ${a.titlu||'anunț'}</a>»
- L232 `→` [arrow-right/glyph] — «viewBox-ului) § dreapta=start, stânga=end, sus/j»
- L301 `⚠` [warn/icon] — «class="alerta">§ date insuficiente — verifică ma»
- L322 `▶` [view/icon] — «-hidden="true">§</span> Vezi anunțul${c.titlu?':»
- L401 `🗺` [map/icon] — «-hidden="true">§</span>'»
- L405 `↑` [arrow-up/glyph] — «Ajustează zona §</button></div>';»
- L411 `➜` [arrow-send/icon] — «-hidden="true">§</span> Trimite bifatele la gril»
- L493 `✓` [check/icon] — «textContent = '§ Ponderi salvate.'; }»

### document.html
- L11 `←` [arrow-left/glyph] — «f="/documente">§ Toate documentele</a></p>»

### dosare.html
- L14 `📂` [folder-open/icon] — «-hidden="true">§</span>»
- L17 `→` [arrow-right/glyph] — «chide wizardul §</a>»
- L31 `↗` [arrow-ext/glyph] — «-hidden="true">§</span> Deschide</button>»
- L32 `✎` [edit/icon] — «-hidden="true">§</span> Redenumește</button>»
- L33 `⬇` [download/icon] — «-hidden="true">§</span> .docx</a>»
- L34 `🗑` [delete/icon] — «-hidden="true">§</span> Șterge</button>»

### feedback_list.html
- L12 `⬇` [download/icon] — «-hidden="true">§</span> Descarcă CSV</a></p>»
- L15 `✎` [edit/icon] — «-hidden="true">§</span>»
- L18 `→` [arrow-right/glyph] — «hide aplicația §</a>»

### flux_livrabile.html
- L25 `✓` [check/icon] — «after{content:"§";font-size:var(--text-sm)}»
- L130 `→` [arrow-right/glyph] — «ncepe un dosar §</a>»
- L130 `➕` [add/icon] — «-hidden="true">§</span> Începe un dosar →</a>»
- L155 `→` [arrow-right/glyph] — «ea (tip × scop § profil § ghid GEV) se fixează a»
- L159 `→` [arrow-right/glyph] — «an>raport Word § pre-completare</span></a>»
- L164 `→` [arrow-right/glyph] — «ncepe un dosar §</a></p>»
- L164 `➕` [add/icon] — «-hidden="true">§</span> Începe un dosar →</a></p»
- L185 `→` [arrow-right/glyph] — «ii) pe 2 etape § 3 abordări § reconciliere.</p>»
- L188 `→` [arrow-right/glyph] — «role">Abordări § reconciliere</div>»
- L194 `→` [arrow-right/glyph] — «</b> (GEV 520) § semnalată, nu blochează.</div>»
- L204 `→` [arrow-right/glyph] — «="v sel">redus § standard</div></div>»
- L207 `→` [arrow-right/glyph] — «000 €</b><span>§ RTN (3 zile lucrătoare)</span><»
- L208 `→` [arrow-right/glyph] — «ciune</b><span>§ RTS (de îndată)</span></div><bu»
- L215 `✓` [check/icon] — «-hidden="true">§</div>»

### grila.html
- L16 `↻` [refresh/icon] — «carcaIndice()">§ Indicele ANEVAR</button>»
- L35 `→` [arrow-right/glyph] — «anunțuri reale § preț/mp orientativ)<br>»
- L65 `→` [arrow-right/glyph] — «hirie de piață § abordarea prin venit</h2>»
- L84 `→` [arrow-right/glyph] — «{nume:"Ofertă§Tranzacție", etapa:"tranzactie"},»
- L114 `→` [arrow-right/glyph] — «{nume:"Ofertă§Contract (negociere)", tip:"procen»
- L175 `✓` [check/icon] — «p class="hint">§ '+Math.min(raw.length,NCOMP)+»
- L253 `🗺` [map/icon] — «te($("t-rez"),'§','Niciun teren găsit','Pentru z»
- L256 `➕` [add/icon] — «"${c.pret_mp}">§ grilă</button>` : '';»
- L259 `↗` [arrow-ext/glyph] — «">Vezi anunțul §</a>${c.nota?' <span class="err"»
- L262 `➕` [add/icon] — «class="hint">„§ grilă" pune €/mp în prima coloan»
- L265 `✓` [check/icon] — «b.textContent="§ adăugat";»
- L299 `🚩` [flag/icon] — «bv>PRAG_BRUT?' §':'');»
- L300 `✓` [check/icon] — «/td><td>${sel?'§ ales':''}</td></tr>`;»
- L308 `⚠` [warn/icon] — «" role="alert">§️ Comparabilul ales are ajustare»
- L318 `➕` [add/icon] — «_potential}')">§ trimite VBP în wizard (metoda v»
- L330 `→` [arrow-right/glyph] — «chide wizardul § Pas 3 § metoda venit.";»
- L330 `✓` [check/icon] — «textContent = "§ trimis ("+fmtRo(vbp)+" EUR). De»

### index.html
- L13 `🗺` [map/icon] — «-hidden="true">§</span> Flux livrabile <span cla»
- L16 `→` [arrow-right/glyph] — «Flux livrabile §</a></p>»
- L21 `→` [arrow-right/glyph] — «t": cont local § dosare salvate § spațiu de lucr»
- L23 `→` [arrow-right/glyph] — «e Homepage nou §</a></p>»
- L27 `🧭` [compass-wizard/icon] — «-hidden="true">§</span> Wizard (UI vechi) <span »
- L28 `→` [arrow-right/glyph] — «cu-pas (adresă § subiect § comparabile § calcul »
- L30 `→` [arrow-right/glyph] — «eschide Wizard §</a></p>»
- L35 `📄` [doc/icon] — «-hidden="true">§</span> Toate documentele proiec»

### result.html
- L7 `←` [arrow-left/glyph] — «i"><a href="/">§ evaluare nouă</a></nav>»
- L33 `📄` [doc/icon] — «-hidden="true">§</span> Descarcă raportul .docx<»
- L34 `📝` [doc-edit/icon] — «-hidden="true">§</span> Raport cu note</a>»
- L37 `→` [arrow-right/glyph] — «: „Salvează ca § PDF").»

### wizard.html
- L42 `→` [arrow-right/glyph] — «t">PDF digital § pre-completează câmpurile (cada»
- L58 `→` [arrow-right/glyph] — «ă§a î§i ș§s ț§t â§a, spațiile și sem»
- L266 `➖` [neutral-minus/glyph] — «/ ⚠️ diferit / § nementionat, plus ce a găsit.»
- L266 `⚠` [warn/icon] — «: ✅ potrivit / §️ diferit / ➖ nementionat, plus »
- L266 `✅` [check-filled/icon] — «și raportează: § potrivit / ⚠️ diferit / ➖ nemen»
- L335 `↔` [arrow-bi/glyph] — «conversia EUR § LEI în termenii de»
- L336 `↻` [refresh/icon] — «ință. Butonul „§ Curs BNR" preia cursul oficial »
- L337 `↻` [refresh/icon] — «"btn-curs-bnr">§ Curs BNR (azi)</button>»
- L362 `📄` [doc/icon] — «d="btn-raport">§ Generează și descarcă raportul »
- L363 `📝` [doc-edit/icon] — «n-raport-demo">§ Raport cu note (demo)</button>»
- L364 `🧾` [audit-receipt/icon] — «id="btn-audit">§ Urmă de audit (.txt)</button>»
- L368 `→` [arrow-right/glyph] — «i „Salvează ca § PDF".</small>»
- L373 `◀` [back/icon] — «t" id="inapoi">§ Înapoi</button>»
- L374 `▶` [view/icon] — «ainte">Înainte §</button>»
- L376 `💾` [save/icon] — «sarelor (.db)">§ Backup dosare</a>»
- L377 `📄` [doc/icon] — «ingură pagină">§ Formular clasic</a>»
- L505 `↗` [arrow-ext/glyph] — «">Vezi anunțul §</a></label>»
- L516 `➖` [neutral-minus/glyph] — «==='') return '§';»
- L607 `✓` [check/icon] — «pus.length ? ("§ completat (verifică): "+pus.joi»
- L683 `⛔` [block/icon] — «=='blocheaza'?'§':'⚠️'} ${a.mesaj}</div>`).join(»
- L683 `⚠` [warn/icon] — «locheaza'?'⛔':'§️'} ${a.mesaj}</div>`).join('');»
- L755 `✓` [check/icon] — «p class="hint">§ Venit brut potențial preluat di»


---
## D. Decizii A (2026-06-07) — plan de rollout

- **Q1 set:** macro pe ~18-20 roluri COMUNE (nu reduc catalogul). 1-off rare = case-by-case.
- **Q2 legacy:** `wizard.html` + `formular.html` = tier-D (retragere #18) -> **SKIP** (15 iconuri nu se convertesc).
- **Q3 glife-text:** săgeți →←↗↑↔ + buline ● rămân tipografie (NU SVG).

### Volum REAL de rollout (după skip legacy)
- **55 iconuri ACTIVE** (roluri comune, pagini ne-legacy) — rollout instant când vine macro-ul.
- **8 iconuri 1-off** (case-by-case): arrow-send, compass-wizard, demo, doc-edit, import-similar, thumb-down, thumb-up.
- **15 iconuri SKIP** (wizard/formular legacy).

### Active pe rol (ținta rollout)
| rol | nr | locații |
|---|---|---|
| `check` | 10 | _feedback.html:163, _feedback.html:164, cont.html:69, descoperire.html:493, flux_livrabile.html:25, flux_livrabile.html:215, grila.html:175, grila.html:265, grila.html:300, grila.html:330 |
| `add` | 7 | incepe.html:21, incepe.html:80, flux_livrabile.html:130, flux_livrabile.html:164, grila.html:256, grila.html:262, grila.html:318 |
| `doc` | 5 | _nav_cross.html:7, aml.html:89, aml.html:90, index.html:35, result.html:33 |
| `warn` | 5 | aml.html:20, incepe.html:85, descoperire.html:75, descoperire.html:301, grila.html:308 |
| `map` | 4 | _nav_cross.html:6, descoperire.html:401, grila.html:253, index.html:13 |
| `import` | 4 | incepe.html:23, incepe.html:142, incepe.html:151, descoperire.html:81 |
| `edit` | 3 | _feedback.html:15, dosare.html:32, feedback_list.html:15 |
| `delete` | 3 | descoperire.html:86, descoperire.html:171, dosare.html:34 |
| `folder-open` | 2 | incepe.html:22, dosare.html:14 |
| `view` | 2 | descoperire.html:172, descoperire.html:322 |
| `download` | 2 | dosare.html:33, feedback_list.html:12 |
| `close` | 1 | _feedback.html:22 |
| `swap` | 1 | _nav_cross.html:3 |
| `help` | 1 | _nav_cross.html:8 |
| `folder` | 1 | incepe.html:77 |
| `calendar` | 1 | incepe.html:128 |
| `search` | 1 | descoperire.html:139 |
| `refresh` | 1 | grila.html:16 |
| `flag` | 1 | grila.html:299 |


---
## E. Mapare rol → macro `_icon.html` (substituție mecanică la GO)

Macro confirmat pe master (22 nume). Folosire: `{% from "_icon.html" import icon %}` + `{{ icon("name","cls") }}`.

### Roluri ACTIVE → icon (toate se mapează; 3 ajustări marcate *)
| rol catalog | `{{ icon(...) }}` | clasă culoare |
|---|---|---|
| add | `icon("add")` | — (currentColor) |
| audit-receipt * | `icon("audit")` | — (currentColor) |
| back | `icon("back")` | — (currentColor) |
| calendar | `icon("calendar")` | — (currentColor) |
| check | `icon("check")` | — (currentColor) |
| check-filled * | `icon("check")` | — (currentColor) |
| close | `icon("close")` | — (currentColor) |
| delete | `icon("delete")` | ico-danger |
| doc | `icon("doc")` | — (currentColor) |
| download | `icon("download")` | — (currentColor) |
| edit | `icon("edit")` | — (currentColor) |
| flag | `icon("flag")` | ico-gold |
| folder | `icon("folder")` | — (currentColor) |
| folder-open * | `icon("folder")` | — (currentColor) |
| help | `icon("help")` | — (currentColor) |
| import | `icon("import")` | — (currentColor) |
| info | `icon("info")` | — (currentColor) |
| map | `icon("map")` | — (currentColor) |
| refresh | `icon("refresh")` | — (currentColor) |
| save | `icon("save")` | — (currentColor) |
| search | `icon("search")` | — (currentColor) |
| swap | `icon("swap")` | — (currentColor) |
| view | `icon("view")` | — (currentColor) |
| warn | `icon("warn")` | ico-gold |

*`folder-open`→`folder`, `check-filled`→`check`, `audit-receipt`→`audit` (macro nu are variante separate).

### 1-off — decizie la GO (nu blochează rollout-ul celor active)
- `thumb-up`: nu e in macro (feedback 👍) — ramane emoji SAU A adauga thumb
- `thumb-down`: nu e in macro (feedback 👎) — ramane emoji SAU A adauga thumb
- `demo`: nu e in macro (🧪) — case-by-case; poate ramane
- `import-similar`: 🔁 — foloseste icon("import") sau ramane; intreb A
- `arrow-send`: ➜ trimite — nu e in macro; poate icon("swap") sau glyph; intreb A
- `doc-edit`: 📝 raport cu note — icon("edit") sau icon("doc"); doar result.html:34 (wizard skip)
- `compass-wizard`: 🧭 — A: ramane ornament _compas.svg, NU converti

### Clase culoare (din _design.css)
- default = `currentColor` (preia navy/alb din context)
- `ico-gold` = accent (warn, flag)
- `ico-danger` = roșu (delete)
