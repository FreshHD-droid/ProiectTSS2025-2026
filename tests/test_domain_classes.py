"""
Validation tests for the supporting domain classes: Cargo, FreightTrain, Route.
Tests cover equivalence partitioning for valid/invalid inputs.
"""

import pytest
from domain import Cargo, FreightTrain, Route
from exceptions import (
    NegativeWeightError,
    InvalidCapacityError,
    InvalidSpeedError,
    NegativeDistanceError,
    InvalidDifficultyError,
)


# ============================================================================
# Cargo
# ============================================================================

class TestCargo:

    def test_valid_cargo(self):
        c = Cargo("Steel", 50.0, is_hazardous=False, is_fragile=False)
        assert c.name == "Steel"
        assert c.weight == 50.0
        assert c.is_hazardous is False
        assert c.is_fragile is False

    def test_cargo_zero_weight(self):
        c = Cargo("Empty container", 0.0)
        assert c.weight == 0.0

    def test_cargo_hazardous_fragile(self):
        c = Cargo("Chemicals", 25.0, is_hazardous=True, is_fragile=True)
        assert c.is_hazardous is True
        assert c.is_fragile is True

    def test_cargo_negative_weight_raises(self):
        with pytest.raises(NegativeWeightError):
            Cargo("Bad", -1.0)

    def test_cargo_repr(self):
        c = Cargo("Glass", 10.0, is_fragile=True)
        r = repr(c)
        assert "Glass" in r
        assert "FRAGILE" in r


# ============================================================================
# FreightTrain
# ============================================================================

class TestFreightTrain:

    def test_valid_train(self):
        t = FreightTrain("T-100", 200.0, 80.0)
        assert t.train_id == "T-100"
        assert t.max_capacity == 200.0
        assert t.base_speed == 80.0

    def test_zero_capacity_raises(self):
        with pytest.raises(InvalidCapacityError):
            FreightTrain("T1", 0, 80)

    def test_negative_capacity_raises(self):
        with pytest.raises(InvalidCapacityError):
            FreightTrain("T1", -10, 80)

    def test_zero_speed_raises(self):
        with pytest.raises(InvalidSpeedError):
            FreightTrain("T1", 100, 0)

    def test_negative_speed_raises(self):
        with pytest.raises(InvalidSpeedError):
            FreightTrain("T1", 100, -5)

    def test_train_repr(self):
        t = FreightTrain("T-100", 200.0, 80.0)
        assert "T-100" in repr(t)


# ============================================================================
# Route
# ============================================================================

class TestRoute:

    def test_valid_route(self):
        r = Route("Bucharest", "Cluj", 450.0, 1.5)
        assert r.origin == "Bucharest"
        assert r.destination == "Cluj"
        assert r.distance == 450.0
        assert r.difficulty_factor == 1.5

    def test_route_default_difficulty(self):
        r = Route("A", "B", 100.0)
        assert r.difficulty_factor == 1.0

    def test_route_zero_distance(self):
        r = Route("A", "A", 0.0)
        assert r.distance == 0.0

    def test_negative_distance_raises(self):
        with pytest.raises(NegativeDistanceError):
            Route("A", "B", -10.0)

    def test_difficulty_below_min_raises(self):
        with pytest.raises(InvalidDifficultyError):
            Route("A", "B", 100, 0.5)

    def test_difficulty_above_max_raises(self):
        with pytest.raises(InvalidDifficultyError):
            Route("A", "B", 100, 3.5)

    def test_difficulty_at_boundaries(self):
        r1 = Route("A", "B", 100, 1.0)
        assert r1.difficulty_factor == 1.0
        r2 = Route("A", "B", 100, 3.0)
        assert r2.difficulty_factor == 3.0

    def test_route_repr(self):
        r = Route("Bucharest", "Cluj", 450.0)
        assert "Bucharest" in repr(r)
        assert "Cluj" in repr(r)
