"""
Teste black-box pentru clasa FreightTrain.

Strategii aplicate:
  - Partitionare in clase de echivalenta (EC)
  - Analiza valorilor de frontiera (BVA)

PARTITIONARE
============

max_capacity: float
  EC1 (invalid):  max_capacity <= 0   => InvalidCapacityError
  EC2 (valid):    max_capacity > 0

base_speed: float
  EC3 (invalid):  base_speed <= 0     => InvalidSpeedError
  EC4 (valid):    base_speed > 0

VALORI DE FRONTIERA
===================

max_capacity: -0.01 (invalid), 0 (invalid, strict pozitiv!), 0.01 (valid)
base_speed:   -0.01 (invalid), 0 (invalid, strict pozitiv!), 0.01 (valid)

Constructorul valideaza max_capacity inainte de base_speed. Cand testam
base_speed, trimitem intotdeauna un max_capacity valid.
"""
import pytest

from domain import FreightTrain
from exceptions.transport_exceptions import (
    InvalidCapacityError,
    InvalidSpeedError,
)


# --- max_capacity: partitionare ---

@pytest.mark.parametrize("capacity", [0.01, 1, 100, 10000])
def test_ec2_capacity_positive_is_accepted(capacity):
    """EC2: max_capacity > 0."""
    train = FreightTrain("T1", capacity, 80.0)
    assert train.max_capacity == capacity


@pytest.mark.parametrize("capacity", [-10, -0.01, 0])
def test_ec1_capacity_non_positive_raises(capacity):
    """EC1: max_capacity <= 0."""
    with pytest.raises(InvalidCapacityError):
        FreightTrain("T1", capacity, 80.0)


# --- max_capacity: frontiera ---

def test_bva_capacity_just_below_zero_raises():
    """Frontiera: -0.01 (invalid)."""
    with pytest.raises(InvalidCapacityError):
        FreightTrain("T1", -0.01, 80.0)


def test_bva_capacity_zero_raises():
    """Frontiera: 0 este invalid (strict pozitiv)."""
    with pytest.raises(InvalidCapacityError):
        FreightTrain("T1", 0, 80.0)


def test_bva_capacity_just_above_zero_is_accepted():
    """Frontiera: 0.01 este valid."""
    train = FreightTrain("T1", 0.01, 80.0)
    assert train.max_capacity == 0.01


# --- base_speed: partitionare ---

@pytest.mark.parametrize("speed", [0.01, 1, 80, 300])
def test_ec4_speed_positive_is_accepted(speed):
    """EC4: base_speed > 0."""
    train = FreightTrain("T1", 100.0, speed)
    assert train.base_speed == speed


@pytest.mark.parametrize("speed", [-10, -0.01, 0])
def test_ec3_speed_non_positive_raises(speed):
    """EC3: base_speed <= 0."""
    with pytest.raises(InvalidSpeedError):
        FreightTrain("T1", 100.0, speed)


# --- base_speed: frontiera ---

def test_bva_speed_just_below_zero_raises():
    """Frontiera: -0.01 (invalid)."""
    with pytest.raises(InvalidSpeedError):
        FreightTrain("T1", 100.0, -0.01)


def test_bva_speed_zero_raises():
    """Frontiera: 0 este invalid (strict pozitiv)."""
    with pytest.raises(InvalidSpeedError):
        FreightTrain("T1", 100.0, 0)


def test_bva_speed_just_above_zero_is_accepted():
    """Frontiera: 0.01 este valid."""
    train = FreightTrain("T1", 100.0, 0.01)
    assert train.base_speed == 0.01
