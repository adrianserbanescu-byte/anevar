# Plan de răspuns la incidente și breșe de date

> **DRAFT — necesită validarea unui jurist GDPR.** Cadru de răspuns la incidente de securitate și breșe de
> date cu caracter personal (GDPR art. 33–34). Adaptat naturii aplicației: **rulare locală, offline**, unde
> **operatorul de date este evaluatorul**. Versiune 2026-06-07.

## 1. Scop și cadru legal
Stabilește pașii de detectare, evaluare, limitare, notificare și înregistrare a incidentelor de securitate
și a breșelor de date personale. Cadru: **Regulamentul (UE) 2016/679 (GDPR) art. 33** (notificarea
autorității — ANSPDCP) și **art. 34** (notificarea persoanelor vizate); Legea 190/2018.

## 2. Roluri
- **Operator de date:** evaluatorul autorizat ANEVAR (deține datele clienților pe stația proprie).
- **Persoană de contact / responsabil incident:** `[nume]` (la AML, „persoana desemnată").
- **Furnizor software:** suport tehnic la incidente legate de aplicație (`[email-suport]`).
- **Sub-procesatori (doar pe text anonimizat):** Anthropic / Perplexity (narativ AI) — vezi DPA
  (`docs/legal/13-DPA-acord-prelucrare-DRAFT.md`).

## 3. Suprafața de risc (specifică acestei aplicații)
| Vector | Risc | Observație |
|--------|------|------------|
| **Stația locală** (furt/pierdere laptop, malware) | expunere `dosar.json`, rapoarte, baza AML — **PII în clar pe disc** | mitigare: **criptare disc (BitLocker)** + parolă OS; vezi `BLOCAT §J33` |
| **Fișierul `.env`** (cheia API) | folosire abuzivă a cheii | a nu se distribui; cheie dedicată cu buget limitat |
| **Backup `.zip`** | copie cu PII | a se păstra criptat / loc sigur |
| **Sub-procesator AI** | text trimis la AI | **doar text anonimizat** (marcaje [CLIENT]/[ADRESA]…); datele AML nu pleacă niciodată |
| **Date AML/RTS** | divulgare (tipping-off) | stocate separat (`aml_confidential`), interdicție de divulgare (Legea 129 art. 38) |

## 4. Procedura (pași)
1. **Detectare & raportare internă** — orice suspiciune (furt dispozitiv, acces neautorizat, malware,
   trimitere greșită de date) se notifică imediat responsabilului de incident.
2. **Triere & limitare (containment)** — izolează stația (deconectează rețea), schimbă parolele/cheile
   afectate (revocă cheia API), oprește răspândirea.
3. **Evaluarea breșei** — stabilește: ce date, câte persoane, ce risc pentru drepturile/libertățile lor
   (confidențialitate/identitate). Notează dacă datele erau **criptate** (reduce riscul).
4. **Notificare ANSPDCP (art. 33)** — dacă breșa **prezintă risc** pentru persoane: notifică autoritatea
   **în max. 72 de ore** de la luarea la cunoștință (formular ANSPDCP), chiar și parțial dacă nu sunt toate
   detaliile. Dacă **nu** prezintă risc → se documentează motivul (fără notificare).
5. **Notificare persoane vizate (art. 34)** — dacă riscul este **ridicat**: informează persoanele afectate,
   clar, despre natura breșei, consecințe probabile și măsuri (model în §6).
6. **Remediere & lecții** — repară cauza, întărește măsurile, actualizează acest plan.
7. **Înregistrare** — orice incident (notificat sau nu) se trece în **Registrul de incidente** (§5).

## 5. Registrul de incidente (șablon)
| Nr. | Data/ora descoperirii | Descriere | Date & persoane afectate | Risc evaluat | Notificat ANSPDCP (data) | Notificate persoane (data) | Măsuri | Status |
|-----|----------------------|-----------|--------------------------|--------------|--------------------------|----------------------------|--------|--------|
| 1 | | | | scăzut/ridicat | da/nu | da/nu | | deschis/închis |

## 6. Model de notificare a persoanei vizate (art. 34)
> Stimată/Stimate `[nume]`, vă informăm că la data de `[dată]` a avut loc un incident de securitate care
> ar fi putut afecta datele dumneavoastră (`[categorii]`) prelucrate în scopul evaluării imobiliare. Natura
> incidentului: `[descriere]`. Consecințe posibile: `[…]`. Măsuri luate: `[…]`. Recomandări: `[…]`. Ne
> puteți contacta la `[contact]`. Aveți dreptul să sesizați ANSPDCP (www.dataprotection.ro).

## 7. Măsuri preventive (recomandate)
Criptarea discului (BitLocker); parolă OS puternică; antivirus la zi; backup criptat; cheie API dedicată cu
buget limitat; rularea **versiunii curente** a aplicației; minimizarea datelor (nu păstra dosare inutile).

> Acest plan este un draft procedural. Conținutul juridic (praguri de risc, formulări de notificare,
> termene) se confirmă cu un jurist GDPR înainte de utilizare.
