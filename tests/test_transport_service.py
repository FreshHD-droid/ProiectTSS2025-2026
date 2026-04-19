"""
Tests for the TransportService.compare_plans() method.

Covers the recommendation logic with equivalence partitioning
and decision coverage for the comparison branches.
"""

import pytest
from domain import Cargo, FreightTrain, Route, TransportPlan
from service import TransportService


def _quick_plan(distance, cost_per_km, delay, cargo_weight=30.0,
                capacity=100.0, speed=100.0, difficulty=1.0,
                hazardous=False, fragile=False):
    """Helper to create a plan with minimal boilerplate."""
    train = FreightTrain("T", capacity, speed)
    route = Route("A", "B", distance, difficulty)
    cargo = [Cargo("C", cargo_weight, is_hazardous=hazardous, is_fragile=fragile)]
    return TransportPlan(train, route, cargo, cost_per_km, delay)


class TestComparePlans:
    """
    Equivalence classes for compare_plans recommendation logic:

      EC1: A cheaper AND faster       -> recommended = 'A'
      EC2: B cheaper AND faster       -> recommended = 'B'
      EC3: A cheaper, equal duration  -> recommended = 'A'
      EC4: equal cost, B faster       -> recommended = 'B'
      EC5: A cheaper, B faster        -> recommended = 'either'
      EC6: all equal                  -> recommended = 'either'
    """

    def test_ec1_a_cheaper_and_faster(self):
        """A has lower cost and shorter duration -> recommend A."""
        plan_a = _quick_plan(distance=500, cost_per_km=2.0, delay=0.0)
        plan_b = _quick_plan(distance=1000, cost_per_km=3.0, delay=2.0)
        result = TransportService.compare_plans(plan_a, plan_b)
        assert result["cheaper"] == "A"
        assert result["faster"] == "A"
        assert result["recommended"] == "A"

    def test_ec2_b_cheaper_and_faster(self):
        """B has lower cost and shorter duration -> recommend B."""
        plan_a = _quick_plan(distance=1000, cost_per_km=3.0, delay=2.0)
        plan_b = _quick_plan(distance=500, cost_per_km=2.0, delay=0.0)
        result = TransportService.compare_plans(plan_a, plan_b)
        assert result["cheaper"] == "B"
        assert result["faster"] == "B"
        assert result["recommended"] == "B"

    def test_ec3_a_cheaper_equal_duration(self):
        """A cheaper, same duration -> recommend A."""
        plan_a = _quick_plan(distance=1000, cost_per_km=1.0, delay=0.0, speed=100)
        plan_b = _quick_plan(distance=1000, cost_per_km=3.0, delay=0.0, speed=100)
        result = TransportService.compare_plans(plan_a, plan_b)
        assert result["cheaper"] == "A"
        assert result["faster"] == "equal"
        assert result["recommended"] == "A"

    def test_ec4_equal_cost_b_faster(self):
        """Same cost, B faster -> recommend B.
        Use different speeds (not delay) to vary duration without affecting cost."""
        plan_a = _quick_plan(distance=1000, cost_per_km=2.0, delay=0.0, speed=50)
        plan_b = _quick_plan(distance=1000, cost_per_km=2.0, delay=0.0, speed=100)
        result = TransportService.compare_plans(plan_a, plan_b)
        assert result["cheaper"] == "equal"
        assert result["faster"] == "B"
        assert result["recommended"] == "B"

    def test_ec5_a_cheaper_b_faster(self):
        """A cheaper but B faster -> recommend 'either'."""
        # A: cheaper (low cost_per_km) but slower (high delay)
        plan_a = _quick_plan(distance=1000, cost_per_km=1.0, delay=20.0, speed=100)
        # B: more expensive but faster (no delay)
        plan_b = _quick_plan(distance=1000, cost_per_km=3.0, delay=0.0, speed=100)
        result = TransportService.compare_plans(plan_a, plan_b)
        assert result["cheaper"] == "A"
        assert result["faster"] == "B"
        assert result["recommended"] == "either"

    def test_ec6_all_equal(self):
        """Identical plans -> recommend 'either'."""
        plan_a = _quick_plan(distance=1000, cost_per_km=2.0, delay=1.0, speed=100)
        plan_b = _quick_plan(distance=1000, cost_per_km=2.0, delay=1.0, speed=100)
        result = TransportService.compare_plans(plan_a, plan_b)
        assert result["cheaper"] == "equal"
        assert result["faster"] == "equal"
        assert result["recommended"] == "either"

    def test_result_contains_numeric_fields(self):
        """Verify the result dict contains all expected numeric fields."""
        plan_a = _quick_plan(distance=500, cost_per_km=2.0, delay=0.0)
        plan_b = _quick_plan(distance=800, cost_per_km=3.0, delay=1.0)
        result = TransportService.compare_plans(plan_a, plan_b)

        assert "cost_a" in result
        assert "cost_b" in result
        assert "duration_a" in result
        assert "duration_b" in result
        assert "load_ratio_a" in result
        assert "load_ratio_b" in result
