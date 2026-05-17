"""
Teste black-box pentru clasa Cargo.

Strategii aplicate:
  - Partitionare in clase de echivalenta (EC)
  - Analiza valorilor de frontiera (BVA)

Parametrul `weight` este singurul cu validare.
Parametrii `name`, `is_hazardous`, `is_fragile` nu au validare
(sunt doar setari de atribut), deci nu necesita partitionare.

PARTITIONARE
============

weight: float
  EC1 (invalid):  weight < 0   => NegativeWeightError
  EC2 (valid):    weight >= 0

VALORI DE FRONTIERA
===================

weight: -0.01 (invalid), 0 (valid, inclus), 0.01 (valid)
"""
import pytest

from domain import Cargo
from exceptions.transport_exceptions import NegativeWeightError


# --- Partitionare in clase de echivalenta ---

@pytest.mark.parametrize("weight", [0, 0.5, 40.0, 999.99])
def test_ec2_weight_non_negative_is_accepted(weight):
    """EC2: orice weight >= 0 este acceptat."""
    cargo = Cargo("Marfa", weight)
    assert cargo.weight == weight


@pytest.mark.parametrize("weight", [-0.01, -5, -1000])
def test_ec1_weight_negative_raises(weight):
    """EC1: weight < 0 => NegativeWeightError."""
    with pytest.raises(NegativeWeightError):
        Cargo("Marfa", weight)


# --- Analiza valorilor de frontiera ---

def test_bva_weight_just_below_zero_raises():
    """Frontiera: -0.01 (just invalid)."""
    with pytest.raises(NegativeWeightError):
        Cargo("Marfa", -0.01)


def test_bva_weight_zero_is_accepted():
    """Frontiera: 0 (inclus in EC2)."""
    cargo = Cargo("Marfa", 0)
    assert cargo.weight == 0


def test_bva_weight_just_above_zero_is_accepted():
    """Frontiera: 0.01 (just valid)."""
    cargo = Cargo("Marfa", 0.01)
    assert cargo.weight == 0.01
