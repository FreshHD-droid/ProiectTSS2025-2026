import pytest

# Se presupun importurile corecte din proiectul tau
from domain import Cargo
from domain import FreightTrain
from domain import Route
from service import RiskEvaluator
from exceptions.transport_exceptions import NegativeDelayError, EmptyCargoListError


@pytest.fixture
def base_train():
    # Capacitate de 100t pentru a face calculele raportului (ratio) evidente
    return FreightTrain("T1", max_capacity=100.0, base_speed=50.0)


# =====================================================================
# PATH 1 & 2: Acoperirea exceptiilor (Statement, Decision, Path)
# =====================================================================
def test_risk_path_negative_delay(base_train):
    evaluator = RiskEvaluator()
    route = Route("A", "B", 100.0)
    cargo_list = [Cargo("C1", 10.0)]

    # Acopera prima decizie if delay_hours < 0: (True)
    with pytest.raises(NegativeDelayError):
        evaluator.evaluate_shipment_risk(cargo_list, base_train, route, -2.0)


def test_risk_path_empty_cargo(base_train):
    evaluator = RiskEvaluator()
    route = Route("A", "B", 100.0)

    # Acopera prima decizie (False) si a doua decizie if not cargo_list: (True)
    with pytest.raises(EmptyCargoListError):
        evaluator.evaluate_shipment_risk([], base_train, route, 0.0)


# =====================================================================
# PATH 3-7: Acoperirea deciziilor, conditiilor si ramurilor principale
# =====================================================================
@pytest.mark.parametrize(
    "is_hazardous, cargo_weight, difficulty, delay, expected_risk, test_id",
    [
        # PATH 3: Conditia 1 (TT) -> Returnare rapida HIGH (Hazardous & Plin)
        # haz > 0 (True) AND ratio 0.8 > 0.7 (True)
        # Statement Coverage: Return-ul din primul if.
        (True, 80.0, 1.0, 0.0, "HIGH", "Path3_Haz_And_Heavy"),

        # PATH 4: Conditia 1 (TF), Conditia 2 (TT) -> HIGH (Rută grea & Întârziere)
        # haz > 0 (True) AND ratio 0.4 > 0.7 (False) -> Se trece mai departe
        # diff 2.5 >= 2.0 (True) AND delay 5 > 4 (True) -> risk = HIGH
        (True, 40.0, 2.5, 5.0, "HIGH", "Path4_Haz_Light_BadRoute_Delayed"),

        # PATH 5: Conditia 1 (FT), Conditia 2 (TF), Decizia finala (True) -> MEDIUM
        # haz > 0 (False) AND ratio 0.8 > 0.7 (ignorata) -> Se trece mai departe
        # diff 2.5 >= 2.0 (True) AND delay 2 > 4 (False) -> ramura ELSE
        # ratio 0.8 > 0.5 (True) -> risk = MEDIUM
        (False, 80.0, 2.5, 2.0, "MEDIUM", "Path5_NotHaz_Heavy_BadRoute_OnTime"),

        # PATH 6: Conditia 1 (F_), Conditia 2 (FT), Decizia finala (False) -> LOW
        # haz > 0 (False) -> Se trece mai departe
        # diff 1.0 >= 2.0 (False) AND delay 5 > 4 (ignorata) -> ramura ELSE
        # ratio 0.4 > 0.5 (False) -> risk = LOW
        (False, 40.0, 1.0, 5.0, "LOW", "Path6_NotHaz_Light_EasyRoute_Delayed"),

        # PATH 7: Conditia 1 (TF), Conditia 2 (F_), Decizia finala (True) -> MEDIUM
        # Extra test pentru condition coverage: haz (True) dar ratio mic (0.6).
        # diff 1.0 >= 2.0 (False) -> intra in ELSE final.
        # ratio 0.6 > 0.5 (True) -> risk = MEDIUM
        (True, 60.0, 1.0, 0.0, "MEDIUM", "Path7_Haz_MediumWeight_EasyRoute_OnTime")
    ]
)
def test_evaluate_shipment_risk_logic_paths(
        base_train, is_hazardous, cargo_weight, difficulty, delay, expected_risk, test_id
):
    evaluator = RiskEvaluator()
    route = Route("A", "B", 100.0, difficulty_factor=difficulty)
    cargo_list = [Cargo("C1", cargo_weight, is_hazardous=is_hazardous)]

    result = evaluator.evaluate_shipment_risk(cargo_list, base_train, route, delay)
    assert result == expected_risk, f"A picat la scenariul: {test_id}"


# =====================================================================
# PATH 8: Test special pentru acoperirea completa a buclei FOR (is_hazardous)
# =====================================================================
def test_risk_path_loop_condition(base_train):
    """
    Acoperă cazul în care avem mai multe mărfuri în listă,
    unele periculoase, altele nu, pentru a valida că decizia
    `if c.is_hazardous:` din interiorul buclei FOR este evaluată T și F în aceeași rulare.
    """
    evaluator = RiskEvaluator()
    route = Route("A", "B", 100.0, difficulty_factor=1.0)
    cargo_list = [
        Cargo("Normal", 30.0, is_hazardous=False),  # c.is_hazardous = False
        Cargo("Periculos", 10.0, is_hazardous=True)  # c.is_hazardous = True
    ]
    # Total = 40t (ratio 0.4). Haz = 10t.
    # Logic: nu atinge 0.7 la ratio. Route diff = 1.0.
    # Intra pe ELSE, ratio 0.4 nu e > 0.5, returneaza LOW.

    assert evaluator.evaluate_shipment_risk(cargo_list, base_train, route, 0.0) == "LOW"