"""
Teste black-box pentru metoda RiskEvaluator.evaluate_shipment_risk.

Strategii aplicate:
  - Partitionare in clase de echivalenta (EC)
  - Analiza valorilor de frontiera (BVA)

INTRARI
=======

cargo_list:
  EC1 (invalid):  lista goala                     => EmptyCargoListError
  EC2 (valid):    lista nevida

delay_hours:
  EC3 (invalid):  delay_hours < 0                 => NegativeDelayError
  EC4 (valid):    delay_hours >= 0
  Frontiera: -0.01 (invalid), 0 (valid, inclus)

train, route: validate de propriile constructoare (preconditie metoda).

IESIRI
======

Functia returneaza una din: "HIGH", "MEDIUM", "LOW".

EC5 (HIGH, regula 1):  hazardous_weight > 0 SI ratio > 0.7
EC6 (HIGH, regula 2):  difficulty_factor >= 2.0 SI delay_hours > 4
EC7 (MEDIUM):          niciuna din regulile HIGH si ratio > 0.5
EC8 (LOW):             niciuna din regulile HIGH si ratio <= 0.5

Frontiere de iesire:
  ratio = 0.7              (NU intra in EC5; conditia este "> 0.7", strict)
  ratio = 0.5              (LIMITA EC7/EC8; "<= 0.5" => LOW)
  difficulty_factor = 2.0  (LIMITA EC6; ">= 2.0" inclus)
  delay_hours = 4          (LIMITA EC6; "> 4" strict)
"""
import pytest

from domain import Cargo, Route
from service.risk_evaluator import RiskEvaluator
from exceptions.transport_exceptions import (
    NegativeDelayError,
    EmptyCargoListError,
)


# ============================================================
# Validari (EC1, EC3) + frontiere validare
# ============================================================

def test_ec1_empty_cargo_list_raises(train_100t_80kmh, route_450_diff1):
    """EC1: cargo_list gol => EmptyCargoListError."""
    with pytest.raises(EmptyCargoListError):
        RiskEvaluator().evaluate_shipment_risk([], train_100t_80kmh, route_450_diff1, 1.0)


@pytest.mark.parametrize("delay", [-0.01, -1, -100])
def test_ec3_delay_negative_raises(
    train_100t_80kmh, route_450_diff1, cargo_normal, delay
):
    """EC3: delay_hours < 0 => NegativeDelayError."""
    with pytest.raises(NegativeDelayError):
        RiskEvaluator().evaluate_shipment_risk([cargo_normal], train_100t_80kmh, route_450_diff1, delay)


def test_bva_delay_just_below_zero_raises(
    train_100t_80kmh, route_450_diff1, cargo_normal
):
    """Frontiera: delay_hours = -0.01 (invalid)."""
    with pytest.raises(NegativeDelayError):
        RiskEvaluator().evaluate_shipment_risk([cargo_normal], train_100t_80kmh, route_450_diff1, -0.01)


def test_bva_delay_zero_is_accepted(
    train_100t_80kmh, route_450_diff1, cargo_normal
):
    """Frontiera: delay_hours = 0 (acceptat, inclus in EC4)."""
    # cargo_normal: 10t pe tren 100t => ratio 0.1; difficulty 1.0
    # nicio regula HIGH; ratio <= 0.5 => LOW
    result = RiskEvaluator().evaluate_shipment_risk([cargo_normal], train_100t_80kmh, route_450_diff1, 0)
    assert result == "LOW"


# ============================================================
# Iesire HIGH via regula 1: hazardous + ratio > 0.7
# ============================================================

def test_ec5_high_when_hazardous_and_ratio_above_07(train_100t_80kmh, route_450_diff1):
    """EC5: marfa periculoasa + raport > 0.7 => HIGH."""
    cargo_list = [Cargo("Periculos", 80.0, is_hazardous=True)]  # ratio = 0.8
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "HIGH"


def test_ec5_high_partial_hazardous_and_ratio_above_07(
    train_100t_80kmh, route_450_diff1
):
    """EC5: macar o marfa periculoasa (mix) + raport > 0.7 => HIGH."""
    cargo_list = [
        Cargo("Marfa", 50.0),
        Cargo("Periculos", 30.0, is_hazardous=True),  # total 80t => ratio 0.8
    ]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "HIGH"


def test_bva_ratio_exactly_07_with_hazardous_is_not_high_via_rule_1(
    train_100t_80kmh, route_450_diff1
):
    """Frontiera: raport = 0.7 EXACT cu marfa periculoasa NU activeaza regula HIGH 1
    (conditia este '> 0.7', strict)."""
    cargo_list = [Cargo("Periculos", 70.0, is_hazardous=True)]  # ratio = 0.7
    # difficulty 1.0, delay 0 => regula 2 nu se aplica
    # ratio 0.7 > 0.5 => MEDIUM
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "MEDIUM"


def test_bva_ratio_just_above_07_with_hazardous_is_high(
    train_100t_80kmh, route_450_diff1
):
    """Frontiera: raport = 0.7 + eps cu marfa periculoasa => HIGH."""
    cargo_list = [Cargo("Periculos", 70.01, is_hazardous=True)]  # ratio = 0.7001
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "HIGH"


# ============================================================
# Iesire HIGH via regula 2: difficulty >= 2.0 + delay > 4
# ============================================================

def test_ec6_high_when_route_difficult_and_delay_long(train_100t_80kmh):
    """EC6: difficulty_factor >= 2.0 SI delay > 4 => HIGH (fara periculos)."""
    route = Route("A", "B", 100.0, difficulty_factor=2.5)
    cargo_list = [Cargo("Marfa", 30.0)]  # ratio = 0.3
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route, 5)
    assert result == "HIGH"


def test_bva_difficulty_exactly_2_with_long_delay_is_high(train_100t_80kmh):
    """Frontiera: difficulty_factor = 2.0 EXACT (>= 2.0 inclus) cu delay > 4 => HIGH."""
    route = Route("A", "B", 100.0, difficulty_factor=2.0)
    cargo_list = [Cargo("Marfa", 30.0)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route, 5)
    assert result == "HIGH"


def test_bva_difficulty_just_below_2_with_long_delay_is_not_high(train_100t_80kmh):
    """Frontiera: difficulty_factor = 1.99 (< 2.0) cu delay > 4 => regula 2 nu activata."""
    route = Route("A", "B", 100.0, difficulty_factor=1.99)
    cargo_list = [Cargo("Marfa", 30.0)]  # ratio = 0.3
    # nicio regula HIGH; ratio 0.3 <= 0.5 => LOW
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route, 5)
    assert result == "LOW"


def test_bva_delay_exactly_4_with_difficult_route_is_not_high_via_rule_2(
    train_100t_80kmh,
):
    """Frontiera: delay = 4 EXACT (NU > 4) cu difficulty >= 2.0 => regula 2 nu activata."""
    route = Route("A", "B", 100.0, difficulty_factor=2.5)
    cargo_list = [Cargo("Marfa", 30.0)]
    # nicio regula HIGH; ratio 0.3 <= 0.5 => LOW
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route, 4)
    assert result == "LOW"


def test_bva_delay_just_above_4_with_difficult_route_is_high(train_100t_80kmh):
    """Frontiera: delay = 4.01 (> 4) cu difficulty >= 2.0 => HIGH."""
    route = Route("A", "B", 100.0, difficulty_factor=2.5)
    cargo_list = [Cargo("Marfa", 30.0)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route, 4.01)
    assert result == "HIGH"


# ============================================================
# Iesire MEDIUM (EC7) si LOW (EC8) + frontiera 0.5
# ============================================================

def test_ec7_medium_when_no_high_rule_but_ratio_above_05(
    train_100t_80kmh, route_450_diff1
):
    """EC7: nicio regula HIGH si ratio > 0.5 => MEDIUM."""
    cargo_list = [Cargo("Marfa", 60.0)]  # ratio = 0.6
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "MEDIUM"


def test_ec8_low_when_no_high_rule_and_ratio_at_or_below_05(
    train_100t_80kmh, route_450_diff1
):
    """EC8: nicio regula HIGH si ratio <= 0.5 => LOW."""
    cargo_list = [Cargo("Marfa", 30.0)]  # ratio = 0.3
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "LOW"


def test_bva_ratio_exactly_05_is_low(train_100t_80kmh, route_450_diff1):
    """Frontiera: raport = 0.5 EXACT (NU > 0.5) => LOW."""
    cargo_list = [Cargo("Marfa", 50.0)]  # ratio = 0.5
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "LOW"


def test_bva_ratio_just_above_05_is_medium(train_100t_80kmh, route_450_diff1):
    """Frontiera: raport = 0.5 + eps (> 0.5) => MEDIUM."""
    cargo_list = [Cargo("Marfa", 50.01)]  # ratio = 0.5001
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "MEDIUM"


# ============================================================
# Cazuri suplimentare (combinatii care NU activeaza regulile HIGH)
# ============================================================

def test_hazardous_with_low_ratio_is_not_high_via_rule_1(
    train_100t_80kmh, route_450_diff1
):
    """Marfa periculoasa cu raport mic (<= 0.7) NU declanseaza regula HIGH 1."""
    cargo_list = [Cargo("Periculos", 30.0, is_hazardous=True)]  # ratio = 0.3
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "LOW"


def test_no_hazardous_with_high_ratio_is_not_high_via_rule_1(
    train_100t_80kmh, route_450_diff1
):
    """Raport > 0.7 fara marfa periculoasa NU declanseaza regula HIGH 1."""
    cargo_list = [Cargo("Marfa", 90.0)]  # ratio = 0.9
    # nicio regula HIGH; ratio > 0.5 => MEDIUM
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "MEDIUM"


def test_fragile_only_does_not_affect_risk(train_100t_80kmh, route_450_diff1):
    """Marfa fragila (fara periculos) NU influenteaza nivelul de risc."""
    cargo_list = [Cargo("Fragil", 30.0, is_fragile=True)]
    # is_fragile NU este folosit in metoda; ratio 0.3 => LOW
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "LOW"


def test_loop_iterates_through_all_cargo_items(train_100t_80kmh, route_450_diff1):
    """Verifica ca loop-ul aduna corect greutatea totala (3 marfuri)."""
    cargo_list = [
        Cargo("A", 30.0),
        Cargo("B", 40.0),
        Cargo("C", 20.0),  # total 90t => ratio 0.9
    ]
    # nicio marfa periculoasa, nicio regula HIGH
    # ratio 0.9 > 0.5 => MEDIUM
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "MEDIUM"
