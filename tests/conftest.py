"""Fixture-uri comune pentru suita de teste."""
import pytest

from domain import Cargo, FreightTrain, Route


@pytest.fixture
def train_100t_80kmh():
    """Tren standard: 100t capacitate, 80 km/h."""
    return FreightTrain("T1", 100.0, 80.0)


@pytest.fixture
def route_450_diff1():
    """Ruta standard: 450 km, dificultate 1.0."""
    return Route("Bucuresti", "Cluj", 450.0, 1.0)


@pytest.fixture
def cargo_normal():
    """Marfa obisnuita: 10t, niciun flag."""
    return Cargo("Marfa", 10.0)
