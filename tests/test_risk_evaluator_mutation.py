"""
Teste suplimentare pentru a omori mutantii non-echivalenti supravietuitori
dupa rularea initiala a mutmut pe `service/risk_evaluator.py`.

Rezultatul rularii initiale (suita BB + WB):
  - 35 mutanti generati
  - 32 omorati (ok_killed)
  - 3 supravietuitori (bad_survived)

Mutantii supravietuitori:
  - Mutant #3  (linia 9) : prefix/sufix "XX" in mesajul NegativeDelayError
  - Mutant #6  (linia 11): prefix/sufix "XX" in mesajul EmptyCargoListError
  - Mutant #18 (linia 25): `hazardous_weight > 0` mutat in `hazardous_weight > 1`

Clasificare:
  - #18 este NON-ECHIVALENT (logic): pentru hazardous_weight = 1 exact, codul
    original returneaza "HIGH" (in conditii de ratio), iar mutantul nu.
  - #3, #6 sunt NON-ECHIVALENTI LA CONTRACT: textul mesajelor de eroare face
    parte din interfata expusa apelantilor (logging, monitoring, UI).
    Functional ar putea fi considerati echivalenti, dar alegem o pozitie
    conservatoare si scriem teste care intaresc contractul.

Cerinta proiectului: scrierea a min. 2 teste suplimentare care sa omoare
2 mutanti non-echivalenti. Acest fisier omoara TOTI 3 (3 teste = depasire).
"""
import pytest

from domain import Cargo
from service.risk_evaluator import RiskEvaluator
from exceptions.transport_exceptions import (
    NegativeDelayError,
    EmptyCargoListError,
)


# ============================================================
# Mutant #18: hazardous_weight > 0  =>  hazardous_weight > 1
# Cale de omorare: testam frontiera hazardous_weight = 1 exact,
# cu ratio > 0.7. Codul original returneaza "HIGH"; mutantul nu.
# ============================================================

def test_kill_mut_18_hazardous_weight_threshold_at_1t(train_100t_80kmh, route_450_diff1):
    """Frontiera: hazardous_weight = 1 exact, cu ratio > 0.7 => "HIGH" (regula 1).

    Setup:
      - tren capacitate 100t
      - cargo: 75t normala + 1t periculoasa => total 76t, haz=1t
      - ratio = 0.76 > 0.7
    Cod original: (1 > 0) AND (0.76 > 0.7) = True => "HIGH"
    Mutant #18:   (1 > 1) AND (0.76 > 0.7) = False => continua pe alta cale
                  => difficulty=1.0 < 2.0, deci D5=F => ratio>0.5 => "MEDIUM"
    Asertia "result == 'HIGH'" omoara mutantul.
    """
    cargo_list = [
        Cargo("Marfa normala", 75.0),
        Cargo("Marfa periculoasa", 1.0, is_hazardous=True),
    ]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "HIGH"


# ============================================================
# Mutant #3: NegativeDelayError mesaj cu prefix/sufix "XX"
# Cale de omorare: verificam ca mesajul incepe cu textul exact specificat.
# ============================================================

def test_kill_mut_3_neg_delay_error_message_prefix(
    train_100t_80kmh, route_450_diff1, cargo_normal
):
    """Mesajul NegativeDelayError trebuie sa inceapa exact cu textul specificat.

    Cod original: mesaj = "Intarzierea nu poate fi negativa: -1"
    Mutant #3:    mesaj = "XXIntarzierea nu poate fi negativa: XX-1"
    Asertia .startswith("Intarzierea") prinde mutantul (mutantul incepe cu "XX").
    """
    with pytest.raises(NegativeDelayError) as exc_info:
        RiskEvaluator().evaluate_shipment_risk([cargo_normal], train_100t_80kmh, route_450_diff1, -1)
    msg = str(exc_info.value)
    assert msg.startswith("Intarzierea nu poate fi negativa")
    # verificam si ca valoarea -1 apare in mesaj (asigurare suplimentara contractului)
    assert "-1" in msg


# ============================================================
# Mutant #6: EmptyCargoListError mesaj cu prefix/sufix "XX"
# Cale de omorare: verificam egalitate stricta a mesajului.
# ============================================================

def test_kill_mut_6_empty_cargo_error_message_exact(train_100t_80kmh, route_450_diff1):
    """Mesajul EmptyCargoListError trebuie sa fie exact "Lista de marfuri nu poate fi goala".

    Cod original: mesaj = "Lista de marfuri nu poate fi goala"
    Mutant #6:    mesaj = "XXLista de marfuri nu poate fi goalaXX"
    Asertia == "..." prinde mutantul (mesajul mutat are caractere "XX" in plus).
    """
    with pytest.raises(EmptyCargoListError) as exc_info:
        RiskEvaluator().evaluate_shipment_risk([], train_100t_80kmh, route_450_diff1, 0)
    msg = str(exc_info.value)
    assert msg == "Lista de marfuri nu poate fi goala"
