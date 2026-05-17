"""
Teste white-box (structurale) pentru evaluate_shipment_risk.

Strategii aplicate:
  1. Statement coverage (acoperire la nivel de instructiune)
  2. Decision/Branch coverage (acoperire la nivel de decizie/ramura)
  3. Condition coverage (acoperire la nivel de conditie)
  4. Independent paths (circuite independente, McCabe)

Subiect testat (SUT): service.risk_evaluator.RiskEvaluator.evaluate_shipment_risk

CONTROL FLOW GRAPH (CFG)
========================
V(G) = e - n + 2 = 25 - 19 + 2 = 8
V(G) = #decizii + 1 = 7 + 1 = 8

Cele 7 puncte de decizie:
  D1     : if delay_hours < 0                                   (simpla)
  D2     : if not cargo_list                                    (simpla)
  D_loop : for c in cargo_list (implicit hasNext)               (simpla)
  D3     : if c.is_hazardous                                    (simpla)
  D4     : if hazardous_weight > 0 and ratio > 0.7              (compusa)
  D5     : if route.difficulty_factor >= 2.0 and delay_hours > 4 (compusa, cu else)
  D6     : if ratio > 0.5                                       (simpla)

NOTA: testele black-box existente (tests/test_risk_evaluator_blackbox.py)
ating deja 100% statement + 100% branch coverage pe SUT. Fisierul curent
ILUSTREAZA EXPLICIT fiecare strategie structurala, pentru raport si pentru
analiza circuitelor independente (cerinta T1).
"""
import pytest

from domain import Cargo, Route
from service.risk_evaluator import RiskEvaluator
from exceptions.transport_exceptions import (
    NegativeDelayError,
    EmptyCargoListError,
)


# ============================================================
# 1. STATEMENT COVERAGE (acoperire la nivel de instructiune)
# Scop: fiecare instructiune executabila este parcursa de cel putin un test.
# ============================================================

def test_stmt_validation_negative_delay(train_100t_80kmh, route_450_diff1, cargo_normal):
    """Acopera linia 8-9: if delay_hours < 0; raise NegativeDelayError."""
    with pytest.raises(NegativeDelayError):
        RiskEvaluator().evaluate_shipment_risk([cargo_normal], train_100t_80kmh, route_450_diff1, -1)


def test_stmt_validation_empty_cargo(train_100t_80kmh, route_450_diff1):
    """Acopera linia 10-11: if not cargo_list; raise EmptyCargoListError."""
    with pytest.raises(EmptyCargoListError):
        RiskEvaluator().evaluate_shipment_risk([], train_100t_80kmh, route_450_diff1, 0)


def test_stmt_full_path_low(train_100t_80kmh, route_450_diff1, cargo_normal):
    """Acopera liniile 14-22, 35 (init, loop fara haz, ratio, ramura LOW)."""
    result = RiskEvaluator().evaluate_shipment_risk([cargo_normal], train_100t_80kmh, route_450_diff1, 0)
    assert result == "LOW"


def test_stmt_hazardous_assignment(train_100t_80kmh, route_450_diff1):
    """Acopera linia 18-19: hazardous_weight += c.weight (cand is_hazardous=True)."""
    cargo_list = [Cargo("Periculos", 30.0, is_hazardous=True)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "LOW"


def test_stmt_high_rule_1(train_100t_80kmh, route_450_diff1):
    """Acopera linia 25-26: return 'HIGH' (rule 1, iesire timpurie)."""
    cargo_list = [Cargo("Periculos", 80.0, is_hazardous=True)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "HIGH"


def test_stmt_high_rule_2(train_100t_80kmh):
    """Acopera linia 29-30: risk = 'HIGH' (rule 2, ramura then a D5)."""
    route = Route("A", "B", 100.0, difficulty_factor=2.5)
    cargo_list = [Cargo("Marfa", 30.0)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route, 5)
    assert result == "HIGH"


def test_stmt_medium(train_100t_80kmh, route_450_diff1):
    """Acopera linia 32-33: if ratio > 0.5: risk = 'MEDIUM'."""
    cargo_list = [Cargo("Marfa", 60.0)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "MEDIUM"


# ============================================================
# 2. DECISION/BRANCH COVERAGE (acoperire la nivel de ramura)
# Scop: fiecare ramura T/F a fiecarei decizii este executata.
# 7 decizii x 2 ramuri = 14 ramuri de acoperit.
# ============================================================

def test_branch_d1_true(train_100t_80kmh, route_450_diff1, cargo_normal):
    """D1 = T (delay_hours < 0 este adevarat)."""
    with pytest.raises(NegativeDelayError):
        RiskEvaluator().evaluate_shipment_risk([cargo_normal], train_100t_80kmh, route_450_diff1, -1)


def test_branch_d1_false(train_100t_80kmh, route_450_diff1, cargo_normal):
    """D1 = F (delay_hours >= 0)."""
    result = RiskEvaluator().evaluate_shipment_risk([cargo_normal], train_100t_80kmh, route_450_diff1, 0)
    assert result is not None


def test_branch_d2_true(train_100t_80kmh, route_450_diff1):
    """D2 = T (cargo_list este gol)."""
    with pytest.raises(EmptyCargoListError):
        RiskEvaluator().evaluate_shipment_risk([], train_100t_80kmh, route_450_diff1, 0)


def test_branch_d2_false(train_100t_80kmh, route_450_diff1, cargo_normal):
    """D2 = F (cargo_list este nevid)."""
    result = RiskEvaluator().evaluate_shipment_risk([cargo_normal], train_100t_80kmh, route_450_diff1, 0)
    assert result is not None


def test_branch_loop_iterates(train_100t_80kmh, route_450_diff1):
    """D_loop = T (cel putin o iteratie) si F (terminare)."""
    cargo_list = [Cargo("A", 10.0), Cargo("B", 20.0)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result is not None


def test_branch_d3_true(train_100t_80kmh, route_450_diff1):
    """D3 = T (c.is_hazardous adevarat)."""
    cargo_list = [Cargo("Periculos", 80.0, is_hazardous=True)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "HIGH"


def test_branch_d3_false(train_100t_80kmh, route_450_diff1):
    """D3 = F (c.is_hazardous fals)."""
    cargo_list = [Cargo("Marfa", 30.0)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "LOW"


def test_branch_d4_true(train_100t_80kmh, route_450_diff1):
    """D4 = T (haz_weight>0 AND ratio>0.7)."""
    cargo_list = [Cargo("Periculos", 80.0, is_hazardous=True)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "HIGH"


def test_branch_d4_false(train_100t_80kmh, route_450_diff1):
    """D4 = F (cel putin o sub-conditie falsa)."""
    cargo_list = [Cargo("Marfa", 90.0)]  # haz=0 deci D4=F indiferent de ratio
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "MEDIUM"


def test_branch_d5_true(train_100t_80kmh):
    """D5 = T (difficulty>=2.0 AND delay>4)."""
    route = Route("A", "B", 100.0, difficulty_factor=2.5)
    cargo_list = [Cargo("Marfa", 30.0)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route, 5)
    assert result == "HIGH"


def test_branch_d5_false(train_100t_80kmh, route_450_diff1, cargo_normal):
    """D5 = F (intra in ramura else)."""
    result = RiskEvaluator().evaluate_shipment_risk([cargo_normal], train_100t_80kmh, route_450_diff1, 0)
    assert result == "LOW"


def test_branch_d6_true(train_100t_80kmh, route_450_diff1):
    """D6 = T (ratio > 0.5)."""
    cargo_list = [Cargo("Marfa", 60.0)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "MEDIUM"


def test_branch_d6_false(train_100t_80kmh, route_450_diff1):
    """D6 = F (ratio <= 0.5)."""
    cargo_list = [Cargo("Marfa", 30.0)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "LOW"


# ============================================================
# 3. CONDITION COVERAGE (acoperire la nivel de conditie)
# Scop: fiecare conditie atomica dintr-o decizie ia atat T cat si F,
#       independent de celelalte.
# Decizii compuse:
#   D4 = (hazardous_weight > 0) AND (ratio > 0.7)
#   D5 = (difficulty_factor >= 2.0) AND (delay_hours > 4)
# Pentru fiecare combinatie de sub-conditii: cel putin un test.
# ============================================================

def test_cond_d4_haz_T_ratio_T(train_100t_80kmh, route_450_diff1):
    """D4: haz>0 = T, ratio>0.7 = T => D4 = T."""
    cargo_list = [Cargo("Periculos", 80.0, is_hazardous=True)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "HIGH"


def test_cond_d4_haz_T_ratio_F(train_100t_80kmh, route_450_diff1):
    """D4: haz>0 = T, ratio>0.7 = F => D4 = F (a doua sub-conditie falsa)."""
    cargo_list = [Cargo("Periculos", 30.0, is_hazardous=True)]  # ratio = 0.3
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "LOW"


def test_cond_d4_haz_F_ratio_T(train_100t_80kmh, route_450_diff1):
    """D4: haz>0 = F, ratio>0.7 = T => D4 = F (prima sub-conditie falsa)."""
    cargo_list = [Cargo("Marfa", 90.0)]  # ratio = 0.9, fara haz
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "MEDIUM"


def test_cond_d4_haz_F_ratio_F(train_100t_80kmh, route_450_diff1):
    """D4: haz>0 = F, ratio>0.7 = F => D4 = F (ambele false)."""
    cargo_list = [Cargo("Marfa", 30.0)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "LOW"


def test_cond_d5_diff_T_delay_T(train_100t_80kmh):
    """D5: diff>=2.0 = T, delay>4 = T => D5 = T."""
    route = Route("A", "B", 100.0, difficulty_factor=2.5)
    cargo_list = [Cargo("Marfa", 30.0)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route, 5)
    assert result == "HIGH"


def test_cond_d5_diff_T_delay_F(train_100t_80kmh):
    """D5: diff>=2.0 = T, delay>4 = F => D5 = F (a doua sub-conditie falsa)."""
    route = Route("A", "B", 100.0, difficulty_factor=2.5)
    cargo_list = [Cargo("Marfa", 30.0)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route, 2)  # delay=2 <= 4
    assert result == "LOW"


def test_cond_d5_diff_F_delay_T(train_100t_80kmh, route_450_diff1):
    """D5: diff>=2.0 = F, delay>4 = T => D5 = F (prima sub-conditie falsa)."""
    # route_450_diff1 are difficulty_factor=1.0
    cargo_list = [Cargo("Marfa", 30.0)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 5)
    assert result == "LOW"


def test_cond_d5_diff_F_delay_F(train_100t_80kmh, route_450_diff1, cargo_normal):
    """D5: diff>=2.0 = F, delay>4 = F => D5 = F (ambele false)."""
    result = RiskEvaluator().evaluate_shipment_risk([cargo_normal], train_100t_80kmh, route_450_diff1, 0)
    assert result == "LOW"


# ============================================================
# 4. INDEPENDENT PATHS (circuite independente — McCabe)
# V(G) = 8 => 8 cai linear independente in CFG.
# Fiecare cale corespunde unei combinatii unice de decizii.
# ============================================================

def test_path_1_d1_true(train_100t_80kmh, route_450_diff1, cargo_normal):
    """P1: START -> D1=T -> raise NegativeDelayError -> EXIT."""
    with pytest.raises(NegativeDelayError):
        RiskEvaluator().evaluate_shipment_risk([cargo_normal], train_100t_80kmh, route_450_diff1, -1)


def test_path_2_d2_true(train_100t_80kmh, route_450_diff1):
    """P2: D1=F -> D2=T -> raise EmptyCargoListError -> EXIT."""
    with pytest.raises(EmptyCargoListError):
        RiskEvaluator().evaluate_shipment_risk([], train_100t_80kmh, route_450_diff1, 0)


def test_path_3_high_rule_2(train_100t_80kmh):
    """P3: D1=F, D2=F, loop=1iter no-haz, D4=F, D5=T -> 'HIGH' (rule 2)."""
    route = Route("A", "B", 100.0, difficulty_factor=2.5)
    cargo_list = [Cargo("Marfa", 30.0)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route, 5)
    assert result == "HIGH"


def test_path_4_medium(train_100t_80kmh, route_450_diff1):
    """P4: D1=F, D2=F, loop=1iter no-haz, D4=F, D5=F, D6=T -> 'MEDIUM'."""
    cargo_list = [Cargo("Marfa", 60.0)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "MEDIUM"


def test_path_5_low(train_100t_80kmh, route_450_diff1):
    """P5: D1=F, D2=F, loop=1iter no-haz, D4=F, D5=F, D6=F -> 'LOW'."""
    cargo_list = [Cargo("Marfa", 30.0)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "LOW"


def test_path_6_high_rule_1(train_100t_80kmh, route_450_diff1):
    """P6: D1=F, D2=F, loop=1iter haz, D4=T -> 'HIGH' (rule 1)."""
    cargo_list = [Cargo("Periculos", 80.0, is_hazardous=True)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "HIGH"


def test_path_7_haz_low_ratio(train_100t_80kmh, route_450_diff1):
    """P7: D1=F, D2=F, loop=1iter haz, D4=F, D5=F, D6=F -> 'LOW' (cu haz dar ratio mic)."""
    cargo_list = [Cargo("Periculos", 30.0, is_hazardous=True)]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "LOW"


def test_path_8_loop_multiple_iterations(train_100t_80kmh, route_450_diff1):
    """P8: D1=F, D2=F, loop=2+ iter (mix de cargo) -> diverse rezultate.
    Demonstreaza ca bucla este parcursa de mai multe ori (acoperire loop)."""
    cargo_list = [
        Cargo("Marfa1", 20.0),
        Cargo("Marfa2", 30.0),
        Cargo("Marfa3", 10.0),
    ]
    # total = 60t, ratio = 0.6 > 0.5 => MEDIUM
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "MEDIUM"
