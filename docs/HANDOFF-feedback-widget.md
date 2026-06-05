# Handoff — In-app tester feedback widget (→ Google Forms)

**Date:** 2026-06-05
**Context:** ANEVAR real-estate valuation app (Flask + Jinja templates, Romanian UI).
Goal: collect feedback from 3–5 non-technical domain-expert testers with minimum friction.
Decision: in-app floating widget that submits directly to a Google Form (testers are online; no manual copy-paste, no backend).

---

## Current state (DONE)

A self-contained feedback widget partial has been created and wired into the header.

**Files:**
- `evaluare-anevar/src/evaluare/web/templates/_feedback.html` — NEW. The whole widget: floating "✎ Feedback" button (fixed, bottom-right), modal dialog, styles (uses existing `_design.css` CSS vars: `--brass`, `--gold`, `--paper`, `--ink`, etc.), and JS.
- `evaluare-anevar/src/evaluare/web/templates/_topbar.html` — EDITED. Added `{% include "_feedback.html" %}` after the closing `</div>` of `.topbar`. Because every page includes `_topbar.html`, the widget shows on all 6 pages (wizard, grila, descoperire, aml, form, result).
- `evaluare-anevar/src/evaluare/web/templates/_footer.html` — REVERTED. The include was briefly here, then moved to the header per user request. Footer is back to original.

**What the widget captures & sends per submission:**
- `message` — free text (the note)
- `page` — the Jinja `{{ pagina }}` value (wizard/grila/descoperire/aml/…)
- `url` — `location.href`
- `sentiment` — 👍 merge / 👎 problemă (optional quick reaction)
- `tester` — name, remembered in `localStorage` so they type it once
- (Google adds the timestamp automatically)

**How it submits:** builds a hidden `<form method="POST" target="fb-sink">` posting to
`https://docs.google.com/forms/d/e/<FORM_ID>/formResponse` into a hidden iframe, so the page never navigates and there's no CORS issue. Submit is fire-and-forget (Google returns an opaque cross-origin response; we show a success message after a short delay).

**Guardrail:** if `FB_CONFIG.formId` is still the placeholder `"FORM_ID"`, the Send button shows a warning instead of posting — so it can't silently fail before it's wired up.

---

## Remaining work (TODO — pick up here)

### 1. Create the Google Form
Create a Google Form titled e.g. "Feedback testare — Evaluare ANEVAR" with **5 questions, in this order**:

| # | Question label | Type |
|---|----------------|------|
| 1 | Mesaj | Paragraph (long text) |
| 2 | Pagină | Short answer |
| 3 | URL | Short answer |
| 4 | Reacție | Short answer |
| 5 | Nume tester | Short answer |

Mark all as **not required** (the widget may send only a reaction with no message).
In the form's **Responses** tab, click the Google Sheets icon → "Create spreadsheet" so all feedback lands in one timestamped sheet.

> Option for the agent: this can be done programmatically with the **Google Forms API**
> (`forms.create` + `batchUpdate` to add items), or interactively via the Claude-in-Chrome
> MCP while the user is logged into Google. Manual creation by the user is also fine — it's ~3 min.

### 2. Extract the field IDs
- **formId:** in the form's normal share URL `https://docs.google.com/forms/d/e/<FORM_ID>/viewform`, copy the long string between `/d/e/` and `/viewform`.
- **entry IDs:** form editor → ⋮ menu → **Get pre-filled link** → put a dummy value in each of the 5 fields → **Get link** → copy. The resulting URL contains `entry.<number>=<dummy>` for each field. Map them by the dummy values you typed.
  - (If using the Forms API instead, each created item returns its `questionId`; the entry param is `entry.<questionId>`.)

### 3. Wire the IDs into the widget
Edit the `FB_CONFIG` object at the top of the `<script>` in `_feedback.html`:
```js
var FB_CONFIG = {
  formId:    "1FAIpQLSxxxxxxxxxxxxxxxxxxxx", // real form ID
  message:   "entry.111111111",
  page:      "entry.222222222",
  url:       "entry.333333333",
  sentiment: "entry.444444444",
  tester:    "entry.555555555"
};
```

### 4. Test end-to-end
- Run the Flask app, open any page, click "✎ Feedback".
- Submit a 👍 with a test message → confirm a new row appears in the linked Google Sheet with the correct page name and URL.
- Test a 👎 with text, and a reaction-only submission (no text).
- Confirm the tester name persists after closing/reopening the browser (localStorage).

### 5. (Optional) polish ideas if desired
- Attach a screenshot of the current screen via `html2canvas` (would need a Form field that accepts the image, or upload elsewhere — Forms file-upload requires sign-in, so a simpler route is to skip images or use a Drive upload).
- Add a one-tap 👍/👎 micro-prompt at the end of the main wizard flow (not just the floating button) to lift response rate.
- Localize success/error copy if any English slipped in (current copy is Romanian).

---

## Quick reference — paths
```
evaluare-anevar/src/evaluare/web/templates/
  _feedback.html   ← widget (edit FB_CONFIG here)
  _topbar.html     ← includes _feedback.html  (header injection point)
  _footer.html     ← original, no longer used for feedback
  _design.css      ← CSS variables the widget styles against
```
Pages that render the widget (all include `_topbar.html`): `wizard.html`, `grila.html`, `descoperire.html`, `aml.html`, `form.html`, `result.html`.
