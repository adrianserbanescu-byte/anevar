# Pasul 3 — Comparabile și calcul

## Grilele de comparabile (tab Comparabile)

Aplicația are **trei grile** de ajustare, în funcție de ce evaluezi:

- **Grilă casă** — pe prețul total
- **Grilă teren** — pe preț pe metru pătrat (€/mp)
- **Grilă chirii** — pe chirie €/mp/lună (alimentează abordarea prin venit)

Fiecare grilă lucrează în **două etape**:

1. **Etapa de tranzacție** — corecții pentru ofertă→tranzacție, drept, finanțare, condiții de
   vânzare, condițiile pieței. Se aplică *compus* pe preț.
2. **Etapa de proprietate** — corecții pentru caracteristicile fizice/juridice. Se aplică *aditiv*.

Aplicația **alege automat** comparabila cu ajustarea brută minimă pe etapa de proprietate.

> ⚠️ **Alertă prudențială:** dacă o comparabilă are ajustarea brută peste **25%** (GEV 520),
> aplicația o semnalează. Nu blochează calculul — tu decizi dacă o păstrezi sau o justifici.

## Cele trei abordări (tab Calcul)

| Abordare | Pe scurt |
|---|---|
| **Cost** | Cost de înlocuire net (CIN) + valoarea terenului. |
| **Comparație** | Valoarea din grila de comparabile. |
| **Venit** | Capitalizare directă sau DCF, din venitul brut potențial. |

La final, **reconcilierea** combină abordările (sau alege una) și dă **valoarea finală**, fără TVA.

## Verifică înainte de a merge mai departe

- Ai cel puțin **3 comparabile** (sub acest prag, calculul de piață se oprește).
- Verifici eventualele **alerte** de la motor (suprafețe, depreciere nejustificată, outlieri).
- Te uiți la **valoarea reconciliată** și la metoda selectată.

---

**Următorul pas:** [Pasul 4 — Generarea raportului →](/documente/ghid-raport)
