# Plan de implementare — Comercializare (tool local premium + AI gateway)

> **Pentru lucrători agentici:** SUB-SKILL: `superpowers:subagent-driven-development` sau
> `superpowers:executing-plans`. Pașii folosesc checkbox (`- [ ]`).
> NOTĂ: proiect cu dependențe externe (Supabase/Stripe/Google) — nu se execută integral
> automat; pașii de *setup cont* îi face omul. Sursa: [4-comercializare.md](4-comercializare.md).

**Goal:** Transformă app-ul desktop într-un produs cu abonament, rutând narativul AI printr-un
gateway propriu care autentifică, metrează (per raport) și facturează.

**Architecture:** App desktop rămâne offline pentru tot (calcul/AML/șablon); doar generarea AI
trece prin gateway (Supabase edge function + Postgres) care ține cheia LLM, validează sesiunea
(max 2/cont), verifică cota și scade 1 raport. Plățile prin Stripe.

**Tech Stack:** Supabase (Auth Google + Postgres + Edge Functions/Deno+TS), Stripe (Checkout +
Customer Portal + webhooks), app desktop Python existent (client nou `GatewayNarrativeClient`).

---

## Faza 0 — Prerechizite (setup extern, le face omul) ~1-2h

- [ ] **0.1** Cont Supabase → proiect nou „evaluare-anevar". Notează `SUPABASE_URL` + `anon key` + `service_role key`.
- [ ] **0.2** Google Cloud → proiect → OAuth consent screen (extern) → credențiale „OAuth client (Desktop)". Notează `client_id` (+ secret).
- [ ] **0.3** Cont Stripe → 1 produs „Pro" cu preț recurent lunar (RON) → notează `price_id`. Activează Customer Portal.
- [ ] **0.4** Cheia LLM (Perplexity) → o pui ca secret în Supabase (`PERPLEXITY_API_KEY`), NU în app.

## Faza 1 — MVP (primul leu)

### Task 1: Schema gateway (Supabase Postgres)

**Files:**
- Create: `gateway/sql/01_schema.sql` (repo nou `evaluare-anevar-gateway`)

- [ ] **Step 1: Scrie schema** (Auth users vine de la Supabase; legăm prin `user_id`)

```sql
create table abonamente (
  user_id uuid primary key references auth.users(id) on delete cascade,
  stripe_customer_id text, stripe_sub_id text,
  status text not null default 'inactiv',         -- activ | inactiv | trial
  treapta text not null default 'pro',
  cota_lunara int not null default 40,
  perioada_start date, reset_la date
);
create table consum (
  id bigserial primary key, user_id uuid references auth.users(id),
  tip text not null,                              -- raport | descoperire | zona
  creat_la timestamptz default now()
);
create table sesiuni (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id), device text, creat_la timestamptz default now(),
  vazut_la timestamptz default now()
);
```

- [ ] **Step 2: Aplică în Supabase** (SQL editor) și verifică tabelele există. Commit fișierul.

### Task 2: Proxy AI (Edge Function) — inima gateway-ului

**Files:**
- Create: `gateway/functions/narativ/index.ts`

- [ ] **Step 1: Scrie funcția** (validează user din JWT Supabase → sesiune ≤2 → cotă → cheamă LLM → scade)

```ts
import { serve } from "https://deno.land/std/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

serve(async (req) => {
  const supa = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE")!);
  const jwt = req.headers.get("Authorization")?.replace("Bearer ", "") ?? "";
  const { data: u } = await supa.auth.getUser(jwt);
  if (!u?.user) return json(401, { error: "neautentificat" });
  const body = await req.json();                              // { device, sesiune_id, prompt, capitol }

  // sesiune: max 2 active; cea curentă trebuie să existe
  const { data: ses } = await supa.from("sesiuni").select("id").eq("user_id", u.user.id)
    .order("vazut_la", { ascending: false });
  if (!ses?.some(s => s.id === body.sesiune_id)) return json(403, { error: "sesiune_invalida" });

  // abonament + cotă
  const { data: ab } = await supa.from("abonamente").select("*").eq("user_id", u.user.id).single();
  if (!ab || ab.status === "inactiv") return json(402, { error: "abonament_inactiv" });
  if (body.capitol === "__raport__") {
    const { count } = await supa.from("consum").select("*", { count: "exact", head: true })
      .eq("user_id", u.user.id).eq("tip", "raport").gte("creat_la", ab.perioada_start);
    if ((count ?? 0) >= ab.cota_lunara) return json(402, { error: "cota_atinsa" });
    await supa.from("consum").insert({ user_id: u.user.id, tip: "raport" });
  }

  // apel LLM cu cheia TA
  const r = await fetch("https://api.perplexity.ai/chat/completions", {
    method: "POST", headers: { Authorization: `Bearer ${Deno.env.get("PERPLEXITY_API_KEY")}`,
      "Content-Type": "application/json" },
    body: JSON.stringify({ model: "sonar", messages: [{ role: "user", content: body.prompt }],
      temperature: 0.2 }),
  });
  const out = await r.json();
  return json(200, { text: out.choices?.[0]?.message?.content ?? "" });
});
const json = (s: number, b: unknown) => new Response(JSON.stringify(b), { status: s,
  headers: { "Content-Type": "application/json" } });
```

- [ ] **Step 2: Deploy** `supabase functions deploy narativ`. Test cu `curl` + un JWT valid → 200 cu text.
- [ ] **Step 3: Commit.**

### Task 3: Stripe — abonament + webhook

**Files:**
- Create: `gateway/functions/stripe-webhook/index.ts`

- [ ] **Step 1: Checkout link** — folosește un Stripe Payment Link (zero cod) pentru MVP; clientul intră → plătește → revine.
- [ ] **Step 2: Webhook** care la `checkout.session.completed` și `customer.subscription.updated` scrie în `abonamente` (status, stripe ids, cota_lunara=40, perioada_start=azi).

```ts
// verifică semnătura Stripe, apoi:
await supa.from("abonamente").upsert({ user_id, stripe_customer_id, stripe_sub_id,
  status: "activ", treapta: "pro", cota_lunara: 40, perioada_start: new Date().toISOString().slice(0,10) });
```

- [ ] **Step 3: Deploy + test** cu un eveniment de test din Stripe → rândul în `abonamente` devine `activ`. Commit.

### Task 4: Desktop — client de gateway (înlocuiește apelul direct Perplexity)

**Files:**
- Create: `src/evaluare/ai/gateway_client.py`
- Modify: `src/evaluare/config.py` (alege gateway dacă există token)
- Test: `tests/test_gateway_client.py`

- [ ] **Step 1: Test (mock pe fetcher)**

```python
def test_gateway_client_trimite_token_si_intoarce_text():
    calls = {}
    def fake_post(url, json, headers):
        calls["url"], calls["auth"] = url, headers.get("Authorization")
        return {"text": "narativ generat"}
    from evaluare.ai.gateway_client import GatewayNarrativeClient
    c = GatewayNarrativeClient(base_url="https://g", token="TKN", sesiune_id="S", device="D", _poster=fake_post)
    assert c.completeaza("scrie capitol 1") == "narativ generat"
    assert calls["auth"] == "Bearer TKN" and "g" in calls["url"]
```

- [ ] **Step 2: Rulează → FAIL** (`pytest tests/test_gateway_client.py -v`).
- [ ] **Step 3: Implementează**

```python
class GatewayNarrativeClient:
    def __init__(self, base_url, token, sesiune_id, device, _poster=None):
        self.base_url, self.token, self.sesiune_id, self.device = base_url, token, sesiune_id, device
        self._poster = _poster or self._post_real
    def completeaza(self, prompt, capitol="__raport__"):
        d = self._poster(f"{self.base_url}/narativ",
            json={"prompt": prompt, "capitol": capitol, "sesiune_id": self.sesiune_id, "device": self.device},
            headers={"Authorization": f"Bearer {self.token}"})
        return d["text"]
    def _post_real(self, url, json, headers):
        import requests; r = requests.post(url, json=json, headers=headers, timeout=30)
        r.raise_for_status(); return r.json()
```

- [ ] **Step 4: Rulează → PASS.** **Step 5: Commit.**

### Task 5: Desktop — login Google (OAuth loopback) + token stocat

**Files:**
- Create: `src/evaluare/auth/google_login.py`, `src/evaluare/web/templates/login.html`
- Modify: `src/evaluare/__main__.py` (la pornire: dacă nu există sesiune validă → pagina /login)

- [ ] **Step 1:** Flux: `/login` → buton „Conectează-te cu Google" → deschide URL-ul Supabase OAuth → redirect pe `http://127.0.0.1:8000/auth/callback` → app primește JWT-ul → creează o sesiune (POST gateway `/sesiune`) → stochează `{token, sesiune_id, device}` criptat lângă exe.
- [ ] **Step 2:** `device` = hash din `platform.node()` + un UUID de instalare salvat local.
- [ ] **Step 3:** Test: callback cu un token fals → se salvează starea de sesiune (mock pe gateway). Commit.

### Task 6: Desktop — rutează narativul + descoperirea prin gateway + UI cotă

**Files:**
- Modify: `src/evaluare/config.py` (returnează `GatewayNarrativeClient` dacă există sesiune)
- Modify: `src/evaluare/ai/narrative.py` (folosește clientul injectat — deja injectabil)
- Modify: `src/evaluare/web/templates/wizard.html` (afișează „cotă rămasă" + mesaje 402/403)

- [ ] **Step 1:** `narrative_client()` → dacă există sesiune locală: `GatewayNarrativeClient`; altfel: None (șablon).
  **Metrare o singură dată/raport:** apelul cu `capitol="__raport__"` se trimite O SINGURĂ DATĂ
  (la începutul generării; el scade cota). Cele 6-7 secțiuni narative folosesc numele lor real
  (`capitol="rezumat"` etc.) → NU scad cota. Astfel un raport = 1 unitate, nu 7.
- [ ] **Step 2:** Mesaje UI pe răspunsuri gateway: `cota_atinsa` → „Ai atins limita lunară — cumpără un pachet"; `sesiune_invalida` → „Cont folosit pe alt dispozitiv — reconectează-te".
- [ ] **Step 3:** Endpoint `GET /api/cota` (app → gateway) → afișează „X/40 rapoarte luna asta". Test + commit.

### Task 7: Verificare end-to-end MVP

- [ ] **Step 1:** Cont nou → plată test Stripe → abonament `activ`.
- [ ] **Step 2:** Login Google în app → generează un raport → gateway scade 1 → cota scade.
- [ ] **Step 3:** Login pe al 3-lea „device" → primul e invalidat → apel AI de pe primul → 403 cu mesaj.
- [ ] **Step 4:** Offline → calcul/AML/șablon merg; AI dă mesaj clar. Commit + tag `v-mvp-comercial`.

## Faza 2 (schiță) — scalare
- Trepte multiple (Solo/Nelimitat) + Stripe Customer Portal (self-service) + pachete (one-time price).
- Magic-link fallback (email). Plan anual. Token de drept semnat pentru grație offline 7-14 zile.
- Reset lunar automat al cotei (cron Supabase). UI cotă + istoric consum.

## Faza 3 (schiță) — maturizare
- Pagină „Sesiuni active / Deconectează dispozitiv". Semnale anti-abuz (review manual).
- Canal de update-uri al exe-ului (verificare versiune). Analitică de utilizare.
- Termeni/GDPR/facturare RO cu jurist+contabil.

## Definition of Done (MVP)
Un evaluator poate: plăti → loga cu Google → genera N rapoarte AI/lună prin gateway → e oprit la
cotă → nu poate partaja (a 3-a sesiune invalidează) → folosește tot offline fără AI.

## Riscuri / dependențe
- Externe: conturi Supabase/Stripe/Google (Faza 0). Fără ele, Faza 1 nu pornește.
- Risc principal: **adopția**, nu tehnologia. MVP-ul există ca să validezi cu 2-3 plătitori.
- De păstrat: anonimizarea înainte de gateway (deja există) → gateway-ul vede doar date anonime.
