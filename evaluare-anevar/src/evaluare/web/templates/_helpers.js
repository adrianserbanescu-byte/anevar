// Helpere JS comune, injectate ca include Jinja (la fel ca _design.css); ruleaza offline in .exe.
// Erau duplicate identic in wizard.html si grila.html.
const $ = id => document.getElementById(id);
// Formatare numerica ro-RO (separator mii ".", zecimale ","); pastreaza 2 zecimale.
function fmtRo(v){ const n=+v; if(!isFinite(n)) return v;
  return n.toLocaleString('ro-RO',{minimumFractionDigits:2, maximumFractionDigits:2}); }
// Date-picker: deschide calendarul la click ORIUNDE in field, nu doar pe iconita native (audit UX #2).
(function(){
  function _enhDate(){
    document.querySelectorAll("input[type=date]").forEach(function(d){
      if(d._pick) return; d._pick = 1;
      d.style.cursor = "pointer";
      d.addEventListener("click", function(){ try{ d.showPicker(); }catch(e){} });
    });
  }
  if(document.readyState === "loading") document.addEventListener("DOMContentLoaded", _enhDate);
  else _enhDate();
})();
