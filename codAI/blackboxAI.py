import pytest

# Presupunem că structura proiectului permite aceste importuri.
# Înlocuiește cu calea corectă dacă modulele sunt în alte foldere (ex: from src.cargo import Cargo)
from domain import Cargo
from domain import FreightTrain
from domain import Route
from domain import TransportPlan
from service import RiskEvaluator

from exceptions.transport_exceptions import (
    NegativeWeightError, InvalidCapacityError, InvalidSpeedError,
    NegativeDistanceError, InvalidDifficultyFactorError,
    NegativeCostError, NegativeDelayError, CapacityExceededError,
    EmptyCargoListError
)


# ==========================================
# TESTE PENTRU CARGO
# ==========================================

@pytest.mark.parametrize("weight, expected_exception", [
    (-10.0, NegativeWeightError),  # EC: Valoare negativa
    (-0.01, NegativeWeightError),  # BVA: Sub limita
    (0.0, None),  # BVA: Pe limita inferioara (valid)
    (0.01, None),  # BVA: Peste limita (valid)
    (25.5, None)  # EC: Valoare pozitiva (valid)
])
def test_cargo_weight_bva_ec(weight, expected_exception):
    if expected_exception:
        with pytest.raises(expected_exception):
            Cargo("Fier", weight)
    else:
        cargo = Cargo("Fier", weight)
        assert cargo.weight == weight


# ==========================================
# TESTE PENTRU FREIGHT TRAIN
# ==========================================

@pytest.mark.parametrize("capacity, expected_exception", [
    (-10.0, InvalidCapacityError),  # EC: Valoare negativa
    (0.0, InvalidCapacityError),  # BVA: Limita invalida (strict pozitiva)
    (0.01, None),  # BVA: Imediat peste limita
    (100.0, None)  # EC: Valoare pozitiva valida
])
def test_train_capacity_bva_ec(capacity, expected_exception):
    if expected_exception:
        with pytest.raises(expected_exception):
            FreightTrain("TR-01", capacity, 80)
    else:
        train = FreightTrain("TR-01", capacity, 80)
        assert train.max_capacity == capacity


@pytest.mark.parametrize("speed, expected_exception", [
    (-5.0, InvalidSpeedError),  # EC: Negativ
    (0.0, InvalidSpeedError),  # BVA: Limita invalida
    (1.0, None),  # BVA: Imediat peste limita
    (120.0, None)  # EC: Valid
])
def test_train_speed_bva_ec(speed, expected_exception):
    if expected_exception:
        with pytest.raises(expected_exception):
            FreightTrain("TR-01", 100, speed)
    else:
        train = FreightTrain("TR-01", 100, speed)
        assert train.base_speed == speed


# ==========================================
# TESTE PENTRU ROUTE
# ==========================================

@pytest.mark.parametrize("distance, expected_exception", [
    (-1.0, NegativeDistanceError),  # BVA: Sub limita
    (0.0, None),  # BVA: Limita (distanta 0 e tehnic permisa de cod)
    (500.0, None)  # EC: Valid
])
def test_route_distance_bva(distance, expected_exception):
    if expected_exception:
        with pytest.raises(expected_exception):
            Route("A", "B", distance)
    else:
        route = Route("A", "B", distance)
        assert route.distance == distance


@pytest.mark.parametrize("difficulty, expected_exception", [
    (0.99, InvalidDifficultyFactorError),  # BVA: Sub limita inferioara
    (1.0, None),  # BVA: Limita inferioara
    (2.0, None),  # EC: Clasa de echivalenta valida (mijloc)
    (3.0, None),  # BVA: Limita superioara
    (3.01, InvalidDifficultyFactorError)  # BVA: Peste limita superioara
])
def test_route_difficulty_bva_ec(difficulty, expected_exception):
    if expected_exception:
        with pytest.raises(expected_exception):
            Route("A", "B", 100, difficulty)
    else:
        route = Route("A", "B", 100, difficulty)
        assert route.difficulty_factor == difficulty


# ==========================================
# TESTE PENTRU TRANSPORT PLAN
# ==========================================

@pytest.fixture
def valid_train():
    return FreightTrain("T1", max_capacity=100.0, base_speed=50.0)


@pytest.fixture
def valid_route():
    return Route("A", "B", distance=200.0, difficulty_factor=1.0)  # Base duration = 4 ore


def test_transport_plan_empty_cargo(valid_train, valid_route):
    with pytest.raises(EmptyCargoListError):
        TransportPlan(valid_train, valid_route, [], 10.0)


def test_transport_plan_capacity_exceeded(valid_train, valid_route):
    # Tren capacitate 100. Punem 100.01 t
    cargo_list = [Cargo("C1", 100.01)]
    with pytest.raises(CapacityExceededError):
        TransportPlan(valid_train, valid_route, cargo_list, 10.0)


@pytest.mark.parametrize("cargo_weight, expected_surcharge_multiplier", [
    (50.0, 0.25),  # BVA: ratio 0.50 (<= 0.5)
    (51.0, 0.10),  # BVA: ratio 0.51 (> 0.5 dar <= 0.8)
    (80.0, 0.10),  # BVA: ratio 0.80 (<= 0.8)
    (81.0, 0.0),  # BVA: ratio 0.81 (> 0.8)
])
def test_weight_surcharge_boundaries(valid_train, valid_route, cargo_weight, expected_surcharge_multiplier):
    # Cost de baza: 200 km * 10 = 2000
    plan = TransportPlan(valid_train, valid_route, [Cargo("C1", cargo_weight)], cost_per_km=10.0)
    expected_surcharge = 2000 * expected_surcharge_multiplier
    assert plan.weight_surcharge() == expected_surcharge


@pytest.mark.parametrize("delay, expected_penalty", [
    (0.0, 0.0),  # BVA: delay 0 (<= 0)
    (0.1, 50.0),  # BVA: delay 0.1 (<= 2)
    (2.0, 50.0),  # BVA: delay 2.0 (<= 2)
    (2.1, 53.0),  # BVA: delay 2.1 (<= 6) -> 50 + (0.1)*30 = 53
    (6.0, 170.0),  # BVA: delay 6.0 (<= 6) -> 50 + 4*30 = 170
    (6.1, 175.0),  # BVA: delay 6.1 (> 6) -> 170 + (0.1)*50 = 175
])
def test_delay_penalty_boundaries(valid_train, valid_route, delay, expected_penalty):
    plan = TransportPlan(valid_train, valid_route, [Cargo("C1", 10.0)], cost_per_km=10.0, delay=delay)
    # Folosim math.isclose pentru posibile probleme de precizie la float-uri
    import math
    assert math.isclose(plan.delay_penalty(), expected_penalty, rel_tol=1e-5)


# ==========================================
# TESTE PENTRU RISK EVALUATOR
# ==========================================

def test_risk_evaluator_validations(valid_train, valid_route):
    evaluator = RiskEvaluator()
    with pytest.raises(NegativeDelayError):
        evaluator.evaluate_shipment_risk([Cargo("C1", 10.0)], valid_train, valid_route, -1.0)

    with pytest.raises(EmptyCargoListError):
        evaluator.evaluate_shipment_risk([], valid_train, valid_route, 0.0)


@pytest.mark.parametrize("haz_weight, total_weight, difficulty, delay, expected_risk", [
    # 1. Risc MAXIM (Marfă periculoasă și tren > 70%)
    (10.0, 71.0, 1.0, 0.0, "HIGH"),  # BVA: ratio 0.71 (> 0.7)
    # 2. Risc MAXIM (Rută dificilă >= 2.0 și delay > 4)
    (0.0, 10.0, 2.0, 4.1, "HIGH"),  # BVA: diff 2.0, delay 4.1 (> 4)
    # 3. Risc MEDIU (Ratio > 0.5, fara hazard si ruta/delay sigure)
    (0.0, 51.0, 1.0, 0.0, "MEDIUM"),  # BVA: ratio 0.51 (> 0.5)
    # 4. Risc LOW (Ratio <= 0.5, condiții normale)
    (0.0, 50.0, 1.0, 0.0, "LOW"),  # BVA: ratio 0.50 (<= 0.5)
])
def test_evaluate_shipment_risk_logic(valid_train, valid_route, haz_weight, total_weight, difficulty, delay,
                                      expected_risk):
    evaluator = RiskEvaluator()
    route = Route("A", "B", 100, difficulty)

    cargo_list = []
    if haz_weight > 0:
        cargo_list.append(Cargo("Haz", haz_weight, is_hazardous=True))
    if total_weight - haz_weight > 0:
        cargo_list.append(Cargo("Normal", total_weight - haz_weight))

    assert evaluator.evaluate_shipment_risk(cargo_list, valid_train, route, delay) == expected_risk