from decimal import Decimal

from evaluare.money import to_money, round_lei, pct


def test_to_money_from_float_and_str():
    assert to_money(919) == Decimal("919")
    assert to_money("1398.9") == Decimal("1398.9")
    assert to_money(128.90) == Decimal("128.90")


def test_round_lei_rounds_to_whole_lei_half_up():
    assert round_lei(Decimal("118459.1")) == Decimal("118459")
    assert round_lei(Decimal("118459.5")) == Decimal("118460")


def test_pct_converts_percentage_to_fraction():
    assert pct(35) == Decimal("0.35")
    assert pct(Decimal("4.71")) == Decimal("0.0471")
