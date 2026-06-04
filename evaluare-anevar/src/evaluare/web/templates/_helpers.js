// Helpere JS comune, injectate ca include Jinja (la fel ca _design.css); ruleaza offline in .exe.
// Erau duplicate identic in wizard.html si grila.html.
const $ = id => document.getElementById(id);
// Formatare numerica ro-RO (separator mii ".", zecimale ","); pastreaza 2 zecimale.
function fmtRo(v){ const n=+v; if(!isFinite(n)) return v;
  return n.toLocaleString('ro-RO',{minimumFractionDigits:2, maximumFractionDigits:2}); }
