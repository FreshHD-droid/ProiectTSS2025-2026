"""
Teste black-box pentru clasa TransportPlan (clasa principala).

Strategii aplicate:
  - Partitionare in clase de echivalenta (EC)
  - Analiza valorilor de frontiera (BVA)

INTRARI CONSTRUCTOR
===================

cargo_list: List[Cargo]
  EC1 (invalid):  lista goala                     => EmptyCargoListError
  EC2 (valid):    total weight <= capacitate
  EC3 (invalid):  total weight > capacitate       => CapacityExceededError
  Frontiera: total = capacity-eps (valid), total = capacity (valid, inclus),
             total = capacity+eps (invalid)

cost_per_km: float
  EC4 (invalid):  < 0  => NegativeCostError
  EC5 (valid):    >= 0
  Frontiera: -0.01 (invalid), 0 (valid, inclus), 0.01 (valid)

delay: float
  EC6  (invalid):  delay < 0            => NegativeDelayError
  EC7  (valid):    delay == 0           (penalizare 0)
  EC8  (valid):    0 < delay <= 2       (penalizare 50 fix)
  EC9  (valid):    2 < delay <= 6       (penalizare 50 + (d-2)*30)
  EC10 (valid):    delay > 6            (penalizare 170 + (d-6)*50)
  Frontiera constructor: -0.01 (invalid), 0 (valid, inclus)
  Frontiera delay_penalty: 0, 0.01, 2, 2.01, 6, 6.01

IESIRI METODE
=============

weight_surcharge() — partitionare pe raport = total_weight / capacitate:
  EC11: raport <= 0.5         => 25% din base_cost
  EC12: 0.5 < raport <= 0.8   => 10% din base_cost
  EC13: raport > 0.8          => 0
  Frontiera: 0.5 (inclus in EC11), 0.5+eps (in EC12),
             0.8 (inclus in EC12), 0.8+eps (in EC13)

delay_penalty() — partitionare pe delay (vezi EC7-EC10 de mai sus)

estimated_duration() — partitionare pe flag-urile marfurilor:
  EC14: nici periculos, nici fragil   => factor 1.0x
  EC15: doar periculos SAU doar fragil => factor 1.1x
  EC16: periculos SI fragil           => factor 1.2x
"""
import pytest

from domain import Cargo, TransportPlan
from exceptions.transport_exceptions import (
    NegativeCostError,
    NegativeDelayError,
    CapacityExceededError,
    EmptyCargoListError,
)


# ============================================================
# cargo_list: partitionare + frontiera
# ============================================================

def test_ec1_empty_cargo_raises(train_100t_80kmh, route_450_diff1):
    """EC1: lista goala => EmptyCargoListError."""
    with pytest.raises(EmptyCargoListError):
        TransportPlan(train_100t_80kmh, route_450_diff1, [], cost_per_km=5.0)


def test_ec2_total_weight_within_capacity_is_accepted(train_100t_80kmh, route_450_diff1):
    """EC2: total_weight < capacitate."""
    plan = TransportPlan(
        train_100t_80kmh, route_450_diff1,
        [Cargo("M", 50.0)], cost_per_km=5.0,
    )
    assert sum(c.weight for c in plan.cargo_list) == 50.0


def test_ec3_total_weight_exceeds_capacity_raises(train_100t_80kmh, route_450_diff1):
    """EC3: total_weight > capacitate."""
    with pytest.raises(CapacityExceededError):
        TransportPlan(
            train_100t_80kmh, route_450_diff1,
            [Cargo("M", 60.0), Cargo("N", 50.0)], cost_per_km=5.0,
        )


def test_bva_total_weight_just_below_capacity_is_accepted(train_100t_80kmh, route_450_diff1):
    """Frontiera: total = capacitate - eps."""
    plan = TransportPlan(
        train_100t_80kmh, route_450_diff1,
        [Cargo("M", 99.99)], cost_per_km=5.0,
    )
    assert sum(c.weight for c in plan.cargo_list) == 99.99


def test_bva_total_weight_equals_capacity_is_accepted(train_100t_80kmh, route_450_diff1):
    """Frontiera: total == capacitate (inclus in EC2)."""
    plan = TransportPlan(
        train_100t_80kmh, route_450_diff1,
        [Cargo("M", 100.0)], cost_per_km=5.0,
    )
    assert sum(c.weight for c in plan.cargo_list) == 100.0


def test_bva_total_weight_just_above_capacity_raises(train_100t_80kmh, route_450_diff1):
    """Frontiera: total = capacitate + eps => CapacityExceededError."""
    with pytest.raises(CapacityExceededError):
        TransportPlan(
            train_100t_80kmh, route_450_diff1,
            [Cargo("M", 100.01)], cost_per_km=5.0,
        )


# ============================================================
# cost_per_km: partitionare + frontiera
# ============================================================

@pytest.mark.parametrize("cost", [0, 0.01, 5.0, 100.0])
def test_ec5_cost_per_km_non_negative_is_accepted(
    train_100t_80kmh, route_450_diff1, cost
):
    """EC5: cost_per_km >= 0."""
    plan = TransportPlan(
        train_100t_80kmh, route_450_diff1,
        [Cargo("M", 10.0)], cost_per_km=cost,
    )
    assert plan.cost_per_km == cost


@pytest.mark.parametrize("cost", [-0.01, -1, -100])
def test_ec4_cost_per_km_negative_raises(
    train_100t_80kmh, route_450_diff1, cost
):
    """EC4: cost_per_km < 0 => NegativeCostError."""
    with pytest.raises(NegativeCostError):
        TransportPlan(
            train_100t_80kmh, route_450_diff1,
            [Cargo("M", 10.0)], cost_per_km=cost,
        )


def test_bva_cost_per_km_just_below_zero_raises(train_100t_80kmh, route_450_diff1):
    """Frontiera: -0.01 (invalid)."""
    with pytest.raises(NegativeCostError):
        TransportPlan(
            train_100t_80kmh, route_450_diff1,
            [Cargo("M", 10.0)], cost_per_km=-0.01,
        )


def test_bva_cost_per_km_zero_is_accepted(train_100t_80kmh, route_450_diff1):
    """Frontiera: 0 (inclus in EC5)."""
    plan = TransportPlan(
        train_100t_80kmh, route_450_diff1,
        [Cargo("M", 10.0)], cost_per_km=0,
    )
    assert plan.cost_per_km == 0


# ============================================================
# delay: partitionare (constructor) + frontiera
# ============================================================

@pytest.mark.parametrize("delay", [0, 0.01, 1, 10])
def test_ec7_10_delay_non_negative_is_accepted(
    train_100t_80kmh, route_450_diff1, delay
):
    """EC7-EC10: delay >= 0 acceptat la constructor."""
    plan = TransportPlan(
        train_100t_80kmh, route_450_diff1,
        [Cargo("M", 10.0)], cost_per_km=5.0, delay=delay,
    )
    assert plan.delay == delay


@pytest.mark.parametrize("delay", [-0.01, -1, -100])
def test_ec6_delay_negative_raises(
    train_100t_80kmh, route_450_diff1, delay
):
    """EC6: delay < 0 => NegativeDelayError."""
    with pytest.raises(NegativeDelayError):
        TransportPlan(
            train_100t_80kmh, route_450_diff1,
            [Cargo("M", 10.0)], cost_per_km=5.0, delay=delay,
        )


def test_bva_delay_just_below_zero_raises(train_100t_80kmh, route_450_diff1):
    """Frontiera: -0.01 (invalid)."""
    with pytest.raises(NegativeDelayError):
        TransportPlan(
            train_100t_80kmh, route_450_diff1,
            [Cargo("M", 10.0)], cost_per_km=5.0, delay=-0.01,
        )


def test_bva_delay_zero_is_accepted(train_100t_80kmh, route_450_diff1):
    """Frontiera: 0 (inclus in EC7)."""
    plan = TransportPlan(
        train_100t_80kmh, route_450_diff1,
        [Cargo("M", 10.0)], cost_per_km=5.0, delay=0,
    )
    assert plan.delay == 0


# ============================================================
# weight_surcharge(): partitionare + frontiera pe raport
# ============================================================

def _plan_with_weight(train, route, weight):
    return TransportPlan(train, route, [Cargo("M", weight)], cost_per_km=5.0)


def test_ec11_surcharge_low_load_is_25_percent(train_100t_80kmh, route_450_diff1):
    """EC11: raport <= 0.5 => 25% din base_cost."""
    plan = _plan_with_weight(train_100t_80kmh, route_450_diff1, 40.0)  # ratio 0.4
    assert plan.weight_surcharge() == pytest.approx(plan.base_cost() * 0.25)


def test_ec12_surcharge_medium_load_is_10_percent(train_100t_80kmh, route_450_diff1):
    """EC12: 0.5 < raport <= 0.8 => 10% din base_cost."""
    plan = _plan_with_weight(train_100t_80kmh, route_450_diff1, 70.0)  # ratio 0.7
    assert plan.weight_surcharge() == pytest.approx(plan.base_cost() * 0.10)


def test_ec13_surcharge_high_load_is_zero(train_100t_80kmh, route_450_diff1):
    """EC13: raport > 0.8 => 0."""
    plan = _plan_with_weight(train_100t_80kmh, route_450_diff1, 90.0)  # ratio 0.9
    assert plan.weight_surcharge() == 0.0


def test_bva_surcharge_ratio_exactly_0_5(train_100t_80kmh, route_450_diff1):
    """Frontiera: raport = 0.5 exact (inclus in EC11)."""
    plan = _plan_with_weight(train_100t_80kmh, route_450_diff1, 50.0)
    assert plan.weight_surcharge() == pytest.approx(plan.base_cost() * 0.25)


def test_bva_surcharge_ratio_just_above_0_5(train_100t_80kmh, route_450_diff1):
    """Frontiera: raport = 0.5 + eps (intra in EC12)."""
    plan = _plan_with_weight(train_100t_80kmh, route_450_diff1, 50.01)
    assert plan.weight_surcharge() == pytest.approx(plan.base_cost() * 0.10)


def test_bva_surcharge_ratio_exactly_0_8(train_100t_80kmh, route_450_diff1):
    """Frontiera: raport = 0.8 exact (inclus in EC12)."""
    plan = _plan_with_weight(train_100t_80kmh, route_450_diff1, 80.0)
    assert plan.weight_surcharge() == pytest.approx(plan.base_cost() * 0.10)


def test_bva_surcharge_ratio_just_above_0_8(train_100t_80kmh, route_450_diff1):
    """Frontiera: raport = 0.8 + eps (intra in EC13)."""
    plan = _plan_with_weight(train_100t_80kmh, route_450_diff1, 80.01)
    assert plan.weight_surcharge() == 0.0


# ============================================================
# delay_penalty(): partitionare + frontiera pe delay
# ============================================================

def _plan_with_delay(train, route, delay):
    return TransportPlan(
        train, route, [Cargo("M", 10.0)], cost_per_km=5.0, delay=delay,
    )


def test_ec7_penalty_zero_delay(train_100t_80kmh, route_450_diff1):
    """EC7: delay == 0 => penalizare 0."""
    plan = _plan_with_delay(train_100t_80kmh, route_450_diff1, 0)
    assert plan.delay_penalty() == 0.0


def test_ec8_penalty_small_delay_is_fixed_50(train_100t_80kmh, route_450_diff1):
    """EC8: 0 < delay <= 2 => 50 fix."""
    plan = _plan_with_delay(train_100t_80kmh, route_450_diff1, 1.5)
    assert plan.delay_penalty() == 50.0


def test_ec9_penalty_medium_delay(train_100t_80kmh, route_450_diff1):
    """EC9: 2 < delay <= 6 => 50 + (d-2)*30."""
    plan = _plan_with_delay(train_100t_80kmh, route_450_diff1, 4)
    assert plan.delay_penalty() == pytest.approx(50 + (4 - 2) * 30)  # 110


def test_ec10_penalty_large_delay(train_100t_80kmh, route_450_diff1):
    """EC10: delay > 6 => 170 + (d-6)*50."""
    plan = _plan_with_delay(train_100t_80kmh, route_450_diff1, 8)
    assert plan.delay_penalty() == pytest.approx(170 + (8 - 6) * 50)  # 270


def test_bva_penalty_just_above_zero_is_50(train_100t_80kmh, route_450_diff1):
    """Frontiera: delay = 0 + eps (intra in EC8)."""
    plan = _plan_with_delay(train_100t_80kmh, route_450_diff1, 0.01)
    assert plan.delay_penalty() == 50.0


def test_bva_penalty_exactly_2h_is_50(train_100t_80kmh, route_450_diff1):
    """Frontiera: delay = 2 exact (inclus in EC8)."""
    plan = _plan_with_delay(train_100t_80kmh, route_450_diff1, 2)
    assert plan.delay_penalty() == 50.0


def test_bva_penalty_just_above_2h(train_100t_80kmh, route_450_diff1):
    """Frontiera: delay = 2 + eps (intra in EC9)."""
    plan = _plan_with_delay(train_100t_80kmh, route_450_diff1, 2.01)
    assert plan.delay_penalty() == pytest.approx(50 + 0.01 * 30)


def test_bva_penalty_exactly_6h(train_100t_80kmh, route_450_diff1):
    """Frontiera: delay = 6 exact (inclus in EC9)."""
    plan = _plan_with_delay(train_100t_80kmh, route_450_diff1, 6)
    assert plan.delay_penalty() == pytest.approx(50 + 4 * 30)  # 170


def test_bva_penalty_just_above_6h(train_100t_80kmh, route_450_diff1):
    """Frontiera: delay = 6 + eps (intra in EC10)."""
    plan = _plan_with_delay(train_100t_80kmh, route_450_diff1, 6.01)
    assert plan.delay_penalty() == pytest.approx(170 + 0.01 * 50)


# ============================================================
# estimated_duration(): partitionare pe flag-urile marfurilor
# ============================================================

def test_ec14_duration_normal_cargo_no_multiplier(train_100t_80kmh, route_450_diff1):
    """EC14: nici periculos, nici fragil => factor 1.0x."""
    plan = TransportPlan(
        train_100t_80kmh, route_450_diff1,
        [Cargo("M", 10.0)], cost_per_km=5.0,
    )
    base = 450 / 80 * 1.0
    assert plan.estimated_duration() == pytest.approx(base)


def test_ec15_duration_hazardous_only_is_10_percent(train_100t_80kmh, route_450_diff1):
    """EC15: doar periculos => factor 1.1x."""
    plan = TransportPlan(
        train_100t_80kmh, route_450_diff1,
        [Cargo("M", 10.0, is_hazardous=True)], cost_per_km=5.0,
    )
    base = 450 / 80 * 1.0 * 1.10
    assert plan.estimated_duration() == pytest.approx(base)


def test_ec15_duration_fragile_only_is_10_percent(train_100t_80kmh, route_450_diff1):
    """EC15: doar fragil => factor 1.1x."""
    plan = TransportPlan(
        train_100t_80kmh, route_450_diff1,
        [Cargo("M", 10.0, is_fragile=True)], cost_per_km=5.0,
    )
    base = 450 / 80 * 1.0 * 1.10
    assert plan.estimated_duration() == pytest.approx(base)


def test_ec16_duration_both_flags_is_20_percent(train_100t_80kmh, route_450_diff1):
    """EC16: periculos SI fragil => factor 1.2x."""
    plan = TransportPlan(
        train_100t_80kmh, route_450_diff1,
        [Cargo("M", 10.0, is_hazardous=True, is_fragile=True)],
        cost_per_km=5.0,
    )
    base = 450 / 80 * 1.0 * 1.20
    assert plan.estimated_duration() == pytest.approx(base)


def test_duration_adds_delay_linearly(train_100t_80kmh, route_450_diff1):
    """Delay-ul se aduna la final (nu e parte din EC, dar verifica formula)."""
    plan = TransportPlan(
        train_100t_80kmh, route_450_diff1,
        [Cargo("M", 10.0)], cost_per_km=5.0, delay=3,
    )
    base = 450 / 80 * 1.0
    assert plan.estimated_duration() == pytest.approx(base + 3)
