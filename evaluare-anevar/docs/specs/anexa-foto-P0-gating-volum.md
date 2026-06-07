# Spec implementare #24 — Anexă foto P0 conformitate (gating volum: 10 poze gratis)

> Decizia Adi (2026-06-07) §C2.24 + §E.22bis: **anexă foto = P0 conformitate SEV 2025**, gating
> **DOAR pe volum** (10 poze gratis, peste = plată). Cuplat cu modelul de preț Pro 299-399 lei/lună
> (decizia §E.20). Baza conformității: vezi [`validare-SEV2025-anexe-si-council.md`](../validare-SEV2025-anexe-si-council.md).
>
> Spec generat în sesiunea C (worktree `anevar-c`) pentru implementare în sesiune B sau loop autonom.
> NU implementează — doar îndrumă.

---

## 1. De ce e P0 (nu feature comercial)

`validare-SEV2025-anexe-si-council.md` confirmă: **GEV 630** + **SEV 230 §120** + **SEV 106 §30.6(l)** cer
**fotografii + documente** în anexele raportului. Un raport fără anexe = neconform pentru bancă/ANAF/instanță.

→ Gating-ul TOTAL ca feature comercial face raportul **incomplet/neconform**. Decizia (a): **deblocăm
atașarea anexelor pe build-ul OFFLINE**, dar cu **gating de volum**: 10 poze gratis, peste = obligă upgrade Pro.

---

## 2. Model de utilizare

### Build OFFLINE (gratuit, single-evaluator)
- **0-10 poze:** atașare liberă, fără cont online, fără limită temporară
- **11+ poze:** blocată (paywall scurt: „pentru 11+ foto, upgrade Pro la 299-399 lei/lună")
- **Acceptă upload, dar:** raportul `.docx` generat NU le include — sunt ținute „în așteptare"
  până userul face upgrade sau le șterge (UX clar, nu „dispar tăcut")

### Build COMERCIAL (Pro tier, abonament activ)
- **Nelimitat** (sau cap practic la 50 poze/dosar pentru anti-abuz — un raport real n-are nevoie de >30)
- Foto procesate: redimensionate la max 1920px (compactare `.docx`)
- Toate apar în secțiunea „Anexe" a raportului

### Build DEMO (showcase, fără cont)
- 5 poze gratis pe **toată sesiunea** (nu per dosar) — pentru ca testerul ad-hoc să vadă feature-ul
- Resetează la închidere

---

## 3. Câmpuri de adăugat în `dosar.json`

Modelul `dosar.json` se extinde cu:

```json
{
  "uuid": "...",
  "wizard": { ... },
  "versiuni": [ ... ],
  "anexe_foto": [
    {
      "id": "uuid-foto-1",
      "nume_fisier": "fatada-est.jpg",
      "marime": 123456,
      "mime": "image/jpeg",
      "uploadat_la": "2026-06-07T15:30:00Z",
      "caption": "Fațadă est, vedere stradală",
      "sectiune": "exterior",         // exterior / interior / acte / alte
      "ordine": 1,                     // index în raport
      "incluse_in_raport": true         // false dacă peste prag și user n-a făcut upgrade
    },
    ...
  ],
  "anexe_documente": [
    {
      "id": "uuid-doc-1",
      "nume_fisier": "extras-CF-12345.pdf",
      "marime": 234567,
      "mime": "application/pdf",
      "uploadat_la": "2026-06-07T15:32:00Z",
      "tip": "extras_CF"               // extras_CF / releveu / plan / CPE / alte
    },
    ...
  ]
}
```

**Fișierele fizice:** stocate în `dosare/<uuid>/anexe/foto/<id>.jpg` și `dosare/<uuid>/anexe/docs/<id>.pdf`.
Numele originale păstrate în `nume_fisier` (NU pe disc — taie path traversal).

---

## 4. Endpoint-uri noi (FastAPI router `curent.py`)

### `POST /api/dosar/{uid}/anexa/foto`
Upload o foto. Body multipart-form sau base64. Validare:
- MIME `image/jpeg` sau `image/png` (refuză `image/svg+xml` — XSS risk)
- Max 5 MB per foto
- Max 10 foto pe dosar pe build OFFLINE → 422 cu mesaj „limită gratis atinsă, upgrade Pro"
- Path traversal: folosesc UUID intern, niciodată nume original pe disc

**Response 200:**
```json
{ "id": "uuid-foto-1", "incluse_in_raport": true, "count_total": 7, "limita": 10 }
```

**Response 422 (paywall):**
```json
{
  "detail": "Limită gratis atinsă (10 foto). Pentru atașare nelimitată, upgrade Pro (299-399 lei/lună).",
  "count_total": 10,
  "limita": 10,
  "upgrade_url": "https://evaluare-anevar.ro/upgrade"   // numai pe build COMERCIAL
}
```

### `POST /api/dosar/{uid}/anexa/foto/{foto_id}/sterge`
Șterge o foto (eliberează slot dacă pe gratis).

### `POST /api/dosar/{uid}/anexa/foto/{foto_id}/caption`
Editează caption-ul unei foto.

### `POST /api/dosar/{uid}/anexa/foto/reordoneaza`
Body: `{ "ordine_noua": ["uuid-foto-3", "uuid-foto-1", "uuid-foto-2"] }`. Reordonează pentru raport.

### `GET /api/dosar/{uid}/anexa/foto/{foto_id}`
Returnează fișierul. `Content-Type: image/jpeg`. **NU expune** path-ul real pe disc.

### `POST /api/dosar/{uid}/anexa/document`
Upload doc PDF/DOCX (extras CF, releveu, CPE). Validare:
- MIME `application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Max 10 MB per doc
- Max 20 docs pe dosar (cap practic, NU paywall)

### `DELETE /api/dosar/{uid}/anexa/document/{doc_id}`
Șterge un doc.

---

## 5. UI flow (UI nou, în `templates/curent/dosar.html`)

Sub-tab **Anexe** (deja există ca rezervare cu upload).

### Layout
```
┌──────────────────────────────────────────────────────────┐
│ Anexe                                                    │
│                                                          │
│ ── Fotografii (5/10 gratis) ──────────────────────────── │
│ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐                                │
│ │1 │ │2 │ │3 │ │4 │ │5 │                                │
│ └──┘ └──┘ └──┘ └──┘ └──┘                                │
│ [+ adaugă foto] [drag & drop]                           │
│                                                          │
│ Captions: editezi sub fiecare foto                       │
│ Ordine: drag în grid                                     │
│                                                          │
│ ⚠ La 11+ foto: paywall card „Upgrade Pro"               │
│                                                          │
│ ── Documente ────────────────────────────────────────── │
│ 📄 extras-CF-12345.pdf (uploaded 15:30)         [×]    │
│ 📄 releveu-cadastral.pdf (uploaded 15:32)       [×]    │
│ [+ adaugă document]                                      │
└──────────────────────────────────────────────────────────┘
```

### Componente
- **Grid foto:** thumbnails 120×120px, captions sub fiecare (input text inline)
- **Counter:** „5/10 gratis" — verde dacă <10, roșu dacă =10
- **Paywall card:** apare la încercarea de a uploada a 11-a foto:
  ```
  ┌────────────────────────────────────────┐
  │ 📸 Limită foto gratis atinsă           │
  │                                        │
  │ Pentru anexe nelimitate, upgrade Pro:  │
  │ • 299-399 lei/lună                     │
  │ • Foto nelimitate                      │
  │ • Narativ AI nelimitat                 │
  │                                        │
  │ [Upgrade Pro] [Continuă fără 11+]      │
  └────────────────────────────────────────┘
  ```
- **Drag & drop zone:** acceptă multiple foto deodată; client-side filtrează MIME

### JS minim necesar
- Upload async (FormData + fetch POST)
- Re-render grid pe success
- Toast la 422 (paywall)
- Drag & drop reorder cu sortable lightweight (nu jQuery UI — dependență minimă)

---

## 6. Integrare în `report/generator.py`

Raportul `.docx` populează **secțiunea Anexe** cu fotografii + documente:

```python
# report/generator.py — pseudo
def render_anexe(doc, ctx):
    if not ctx.anexe_foto and not ctx.anexe_documente:
        return  # secțiune lipsă = neconform GEV 630, dar nu blocăm dacă userul forțează
    doc.add_heading("ANEXE", level=1)

    # 1. Fotografii (ordinate per ordine_noua)
    if ctx.anexe_foto:
        doc.add_heading("Fotografii", level=2)
        for foto in sorted([f for f in ctx.anexe_foto if f.incluse_in_raport], key=lambda x: x.ordine):
            doc.add_picture(foto_path(foto.id), width=Inches(5))
            if foto.caption:
                doc.add_paragraph(foto.caption, style="Caption")

    # 2. Documente (referențiate, nu inserate)
    if ctx.anexe_documente:
        doc.add_heading("Documente atașate", level=2)
        for d in ctx.anexe_documente:
            doc.add_paragraph(f"- {d.tip}: {d.nume_fisier}", style="List Bullet")
```

**Atenție:** fotografiile nedeînchise_în_raport (caz: 11+ pe gratis, neupload-uite Pro) **NU intră în
`.docx`** — dar rămân în folder. Avertisment în raport: „⚠ N foto încă în așteptare; upgrade pentru
includere".

---

## 7. Test cases

### Backend (pytest)
- `test_upload_foto_pe_gratis_pana_la_10` — happy path
- `test_upload_foto_11_pe_gratis_intoarce_422_paywall`
- `test_upload_foto_pe_pro_nelimitata` — env `ANEVAR_COMMERCIAL_BUILD=1` + cont activ
- `test_upload_foto_mime_invalid` — SVG/EXE/PHP → 415
- `test_upload_foto_marime_excesiva` — >5MB → 413
- `test_sterge_foto_elibereaza_slot` — după ștergere, contor decrement
- `test_caption_edit` — happy path
- `test_reordoneaza_foto` — happy path
- `test_path_traversal_in_nume_fisier` — `../etc/passwd` ca nume → respins
- `test_concurrent_uploads_nu_dezpasesc_limita` — race condition (lock pe `anexe_foto[]`)

### Frontend (Playwright e2e)
- `test_e2e_upload_foto_drag_drop` — drag → grid populat
- `test_e2e_paywall_la_a_11a_foto` — apare cardul + buton Upgrade
- `test_e2e_reorder_drag` — schimbă ordinea + persistă
- `test_e2e_raport_docx_include_foto` — generează raport, verifică `.docx` conține `<w:drawing>`

### Conformitate
- `test_raport_fara_foto_marcheaza_neconformitate` — secțiune lipsă → avertisment în raport + log

---

## 8. Migrare dosare existente

Dosarele actuale (înainte de feature) NU au `anexe_foto` și `anexe_documente`. Compatibilitate înapoi:
```python
# la incarcare:
dosar.setdefault("anexe_foto", [])
dosar.setdefault("anexe_documente", [])
```

NU rescriem `dosar.json` proactiv — se adaugă la prima editare. Idempotent.

---

## 9. Comportament când contul comercial expiră

(Pentru build COMERCIAL după lansare):
- Foto deja în dosar = rămân (nu retroactiv șterse)
- Foto noi = limită gratis (10/dosar)
- Pe regenerare raport vechi (cu >10 foto): se folosesc cele deja salvate (nu re-validare)

---

## 10. Anti-abuz comercial

Riscul: user creează 1 dosar nou pentru fiecare 10 poze (efectiv unlimited gratis).

Mitigare:
- Trigger paywall = **cumul pe identitate** (CNP/CUI client + scop + tip_proprietate)
- Aceleași 6 câmpuri ca `CAMPURI_IDENTITATE` din ADR-003
- „Dosar nou cu aceeași identitate" = clonă, contează pe același cumul

Implementare: tabel `consum_anexe` în `dosare_fs.py`:
```json
{
  "identitate_hash": "sha256(CNP+scop+tip+...)",
  "foto_uploaded_total": 7,
  "ultima_uploadare": "2026-06-07T..."
}
```

Limit: **20 foto pe identitate** (nu pe dosar individual). 10 pe primul dosar, încă 10 pe al doilea
clonă, apoi paywall.

---

## 11. Roadmap implementare (faze)

### Faza 1 — MVP backend (cel mai mic livrabil care „bifează" P0 conformitate)
- [ ] Endpoint POST/DELETE foto cu gating contor simplu (per dosar, fără identitate)
- [ ] Storage în `dosare/<uid>/anexe/foto/`
- [ ] `dosar.json` extins cu `anexe_foto[]`
- [ ] Integrare în `report/generator.py` (secțiune Anexe simplă)
- [ ] 5 teste backend de bază
- [ ] **NU UI complet** — endpoint-uri callable cu curl/Postman

**Estimat:** 1 zi de cod + 1 zi teste.

### Faza 2 — UI complet
- [ ] Grid foto + drag/drop + captions + reorder în `dosar.html`
- [ ] Paywall card (template + JS)
- [ ] 3 teste Playwright e2e

**Estimat:** 1-2 zile.

### Faza 3 — Documente
- [ ] Endpoint POST/DELETE document
- [ ] UI list în `dosar.html`
- [ ] Integrare în raport (referențiat, nu inclus)

**Estimat:** 0.5 zi.

### Faza 4 — Anti-abuz comercial (când lansezi Pro)
- [ ] Cumul pe identitate
- [ ] Hook în `creeaza_dosar` să citească consum
- [ ] Migrare schema `consum_anexe`

**Estimat:** 1 zi (depinde de finalizarea ADR-003 enforcement).

---

## 12. Cuplaj cu alte decizii

- **#10 lock identitate HIBRID TRIPLU** (ADR-003) — `identitate_hash` din §10 anti-abuz folosește
  EXACT setul de câmpuri tare. **Blocant:** anti-abuz depinde de ADR-003 Action Items 4-5.
- **#20 pricing Pro 299-399 lei** — paywall card afișează prețul exact. **Decis ✅**.
- **#7 conturi Supabase + Stripe** — paywall butonul „Upgrade" deschide checkout Stripe. **Pending Adi.**
- **#21 ordine comercială** — validare cu evaluatori PRIMA → tier Pro live abia după validare. **Pending Adi.**

---

## 13. Acceptare

Feature #24 considerat FINISHED (Faza 1 + Faza 2) când:
- [ ] Endpoint-urile foto funcționale + 5 teste backend verzi
- [ ] UI nou (`dosar.html`) cu upload + grid + paywall card
- [ ] Raport `.docx` include secțiunea Anexe cu foto
- [ ] 3 teste e2e Playwright verzi
- [ ] Counter „N/10 gratis" funcțional
- [ ] Build offline ascunde Upgrade button (per decizia #15)
- [ ] Documentat în `docs/specs/` (acest fișier deja există)
- [ ] Task `impl-anexa-foto-P0` marcat `status=done` în `.memplan/inbox/tasks.mem`
- [ ] Decizia #24 marcată `status=resolved-implemented` în `.memplan/decisions/log.mem`

Faza 3-4 sunt separate, după §B.7 conturi Stripe + §A.21 validare evaluatori.

---

*Generat în sesiunea C (worktree `anevar-c`, ramura `sesiune-c`) — docs only, fără editări de cod.*
