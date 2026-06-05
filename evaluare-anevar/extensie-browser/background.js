// Service worker minimal (Manifest V3). Logica e in content.js; acesta e aici doar
// pentru a satisface manifestul si pentru extinderi viitoare (ex. badge, context menu).
chrome.runtime.onInstalled.addListener(() => {
  console.log("Import anunț → Evaluare ANEVAR instalat.");
});
