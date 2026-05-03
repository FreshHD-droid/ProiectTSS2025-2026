"""
Teste black-box pentru clasa Route.

Strategii aplicate:
  - Partitionare in clase de echivalenta (EC)
  - Analiza valorilor de frontiera (BVA)

PARTITIONARE
============

distance: float
  EC1 (invalid):  distance < 0     => NegativeDistanceError
  EC2 (valid):    distance >= 0

difficulty_factor: float
  EC3 (invalid):  factor < 1.0     => InvalidDifficultyFactorError
  EC4 (valid):    1.0 <= factor <= 3.0
  EC5 (invalid):  factor > 3.0     => InvalidDifficultyFactorError

VALORI DE FRONTIERA
===================

distance:          -0.01 (invalid), 0 (valid, inclus), 0.01 (valid)
difficulty_factor: 0.99 (invalid), 1.0 (valid, inclus), 1.01 (valid),
                   2.99 (valid), 3.0 (valid, inclus), 3.01 (invalid)
"""
import pytest

from domain import Route
from exceptions.transport_exceptions import (
    NegativeDistanceError,
    InvalidDifficultyFactorError,
)


# --- distance: partitionare ---

@pytest.mark.parametrize("distance", [0, 0.01, 100, 10000])
def test_ec2_distance_non_negative_is_accepted(distance):
    """EC2: distance >= 0."""
    route = Route("A", "B", distance)
    assert route.distance == distance


@pytest.mark.parametrize("distance", [-0.01, -10, -1000])
def test_ec1_distance_negative_raises(distance):
    """EC1: distance < 0."""
    with pytest.raises(NegativeDistanceError):
        Route("A", "B", distance)


# --- distance: frontiera ---

def test_bva_distance_just_below_zero_raises():
    """Frontiera: -0.01 (invalid)."""
    with pytest.raises(NegativeDistanceError):
        Route("A", "B", -0.01)


def test_bva_distance_zero_is_accepted():
    """Frontiera: 0 (inclus in EC2)."""
    route = Route("A", "B", 0)
    assert route.distance == 0


def test_bva_distance_just_above_zero_is_accepted():
    """Frontiera: 0.01 (valid)."""
    route = Route("A", "B", 0.01)
    assert route.distance == 0.01


# --- difficulty_factor: partitionare ---

@pytest.mark.parametrize("factor", [1.0, 1.5, 2.0, 2.5, 3.0])
def test_ec4_difficulty_in_range_is_accepted(factor):
    """EC4: factor in [1.0, 3.0]."""
    route = Route("A", "B", 100, factor)
    assert route.difficulty_factor == factor


@pytest.mark.parametrize("factor", [0, 0.5, 0.99])
def test_ec3_difficulty_below_range_raises(factor):
    """EC3: factor < 1.0."""
    with pytest.raises(InvalidDifficultyFactorError):
        Route("A", "B", 100, factor)


@pytest.mark.parametrize("factor", [3.01, 5, 10])
def test_ec5_difficulty_above_range_raises(factor):
    """EC5: factor > 3.0."""
    with pytest.raises(InvalidDifficultyFactorError):
        Route("A", "B", 100, factor)


# --- difficulty_factor: frontiera ---

def test_bva_difficulty_just_below_one_raises():
    """Frontiera: 0.99 (invalid)."""
    with pytest.raises(InvalidDifficultyFactorError):
        Route("A", "B", 100, 0.99)


def test_bva_difficulty_one_is_accepted():
    """Frontiera: 1.0 (inclus in EC4)."""
    route = Route("A", "B", 100, 1.0)
    assert route.difficulty_factor == 1.0


def test_bva_difficulty_just_above_one_is_accepted():
    """Frontiera: 1.01 (valid)."""
    route = Route("A", "B", 100, 1.01)
    assert route.difficulty_factor == 1.01


def test_bva_difficulty_just_below_three_is_accepted():
    """Frontiera: 2.99 (valid)."""
    route = Route("A", "B", 100, 2.99)
    assert route.difficulty_factor == 2.99


def test_bva_difficulty_three_is_accepted():
    """Frontiera: 3.0 (inclus in EC4)."""
    route = Route("A", "B", 100, 3.0)
    assert route.difficulty_factor == 3.0


def test_bva_difficulty_just_above_three_raises():
    """Frontiera: 3.01 (invalid)."""
    with pytest.raises(InvalidDifficultyFactorError):
        Route("A", "B", 100, 3.01)
