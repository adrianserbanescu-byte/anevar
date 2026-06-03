"""Praguri si termene legale AML (constante de configurare, cu articolul sursa)."""
from __future__ import annotations

from decimal import Decimal

# Beneficiar real: control prin detinere > 25% (>=25% + 1 actiune) — Legea 129/2019 art. 4(2)(a)(1)
PRAG_BENEFICIAR_REAL = Decimal("0.25")

# Raportarea tranzactiilor cu numerar — Legea art. 7(1); Norme art. 20(1)
PRAG_NUMERAR_EUR = Decimal("10000")

# KYC la tranzactie ocazionala — Legea art. 13(1)(b)(1)
PRAG_TRANZ_OCAZIONALA_EUR = Decimal("15000")

# Anti-fragmentare: transe sub acest prag, cu elemente comune — Legea art. 7(4)
PRAG_ANTIFRAGMENTARE_EUR = Decimal("15000")

# Transfer de fonduri care declanseaza KYC — Legea art. 13(1)(b)(2)
PRAG_TRANSFER_FONDURI_EUR = Decimal("1000")

# PEP ramane relevant cel putin 12 luni dupa incetarea functiei — Legea art. 3(6), art. 17(1)(c)
PERIOADA_POST_PEP_LUNI = 12

# Pastrarea documentelor — Legea art. 21(1); Norme art. 22(2)
RETENTIE_ANI = 5
RETENTIE_PRELUNGIRE_MAX_ANI = 5  # Legea art. 21(3)

# Termen raportare numerar — Legea art. 7(7); Norme art. 20
TERMEN_RTN_ZILE_LUCRATOARE = 3

# Suspendarea tranzactiei dupa RTS — Legea art. 8(3)
SUSPENDARE_ORE = 24

# Audit independent obligatoriu daca se depasesc cel putin 2 din 3 praguri — Norme art. 9
PRAG_AUDIT_ACTIVE_LEI = Decimal("16000000")
PRAG_AUDIT_CA_LEI = Decimal("32000000")
PRAG_AUDIT_SALARIATI = 50
