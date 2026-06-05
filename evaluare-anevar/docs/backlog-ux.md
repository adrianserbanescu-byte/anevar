# Backlog UX (recomandări neimplementate)

Recomandări reținute din auditul `/design:ux-copy` (toate paginile), neimplementate
fiindcă ating navigarea/etichete în mai multe locuri și necesită confirmare.

## UX-copy — de confirmat înainte de implementare

1. **„Wizard" e jargon englez în navigare.**
   - Propunere: redenumire în „Evaluare" sau „Pas cu pas".
   - Impact: `_topbar.html` (link nav), `wizard.html` (titlu `<title>`, antet), eventual
     referințe „wizard" în texte-ajutor. Necesită aliniere peste tot ca să rămână consecvent.

2. **Inconsecvență „Grile" (navigare) vs „Grilă" (titluri de pagină).**
   - Propunere: uniformizează terminologia (ex. nav „Grile", titluri „Grilă de …").
   - Impact: `_topbar.html`, `grila.html`.

3. **Pagina Descoperire nu are stare goală (empty state) la „Rezultate".**
   - Propunere: text inițial „Niciun rezultat încă. Apasă «Caută comparabile» pentru a începe."
   - Impact: `descoperire.html` (div `#rezultate`).

## Implementate deja (referință)
- Mesaje de eroare după tiparul *Ce s-a întâmplat + Cum repari* (wizard/grilă/aml/form).
- Link descriptiv „Vezi anunțul ↗" în loc de „link".
- Consecvență stări de încărcare („Se caută…").
- Fără expunerea excepției JS brute în UI.

> Notă: copy-ul juridic (banner AML, confirmare RTS/RTN — Legea 129/2019) și cel metodologic
> (SEV/GEV, praguri prudențiale) NU se modifică aici — sunt bucket B (evaluator) / C (jurist).
