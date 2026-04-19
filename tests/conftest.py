import pytest
from domain import Cargo, FreightTrain, Route, TransportPlan


@pytest.fixture
def make_plan():
    """
    Factory fixture to create a TransportPlan with controlled parameters.
    Defaults: capacity=100t, speed=100km/h, distance=1000km, difficulty=1.0,
              one cargo of 30t (normal), cost_per_km=2.0, delay=0.
    """

    def _make_plan(
        capacity=100.0,
        speed=100.0,
        distance=1000.0,
        difficulty=1.0,
        cargo_weights=None,
        hazardous_flags=None,
        fragile_flags=None,
        cost_per_km=2.0,
        delay=0.0,
    ):
        train = FreightTrain("T-TEST", capacity, speed)
        route = Route("Origin", "Destination", distance, difficulty)

        if cargo_weights is None:
            cargo_weights = [30.0]
        if hazardous_flags is None:
            hazardous_flags = [False] * len(cargo_weights)
        if fragile_flags is None:
            fragile_flags = [False] * len(cargo_weights)

        cargo_list = [
            Cargo(f"Cargo_{i}", w, is_hazardous=hazardous_flags[i], is_fragile=fragile_flags[i])
            for i, w in enumerate(cargo_weights)
        ]

        return TransportPlan(train, route, cargo_list, cost_per_km, delay)

    return _make_plan
