# Documentație - Proiect complet (Etapele 1/3 + 2/3 + 3/3)

> Disciplina: **Testarea Sistemelor Software**, FMI, anul III, sem. II, an univ. 2025-2026
> Tema aleasă: **T1 - Testare unitară în Python**
> Etape documentate: **1/3 (black-box)** + **2/3 (white-box)** + **3/3 (mutation testing)** pe SUT-ul principal `evaluate_shipment_risk`.

---

## 1. Informații generale

| Câmp | Valoare                                                                         |
|---|---------------------------------------------------------------------------------|
| Aplicația | Transport Feroviar de Marfă (CLI Python)                                        |
| Limbaj | Python 3.13.2                                                                   |
| Framework de test | pytest 9.0.2                                                                    |
| Strategii aplicate | EC, BVA (black-box) + Statement, Branch, Condition coverage, Circuite independente / McCabe (white-box) + Mutation testing (etapa 3/3) |
| Număr total teste | **164** (125 BB + 36 WB + 3 mutation, toate trec)                                |
| Mutation score final | **100%** (35/35 mutanți omorâți)                                              |
| Repository | https://github.com/FreshHD-droid/ProiectTSS2025-2026                            |
| Echipa | Marcu George Robert, Brișiț Mario Vlad                                          |
| Data raportării | 24.04.2026                                                                      |

---

## 2. Aplicația testată

**Transport Feroviar de Marfă** este o aplicație CLI care modelează planificarea transportului feroviar. Permite definirea trenurilor de marfă, rutelor, mărfurilor și planurilor de transport, calcul automat al costurilor (cost de bază, suprataxă în funcție de încărcare, penalizare de întârziere), estimarea duratei și compararea a două planuri.

Arhitectura este organizată pe straturi:

| Strat | Locație | Rol |
|---|---|---|
| Domeniu | `domain/` | Entitățile de afaceri: `Cargo`, `FreightTrain`, `Route`, `TransportPlan`. Conțin invarianții și regulile de validare. |
| Servicii | `service/` | Logică pe mai multe entități: `TransportService.compare_plans`, `evaluate_shipment_risk`. |
| Excepții | `exceptions/` | 9 excepții personalizate, toate moștenesc `ValueError`. |
| UI | `ui/cli.py` | Interfață linie de comandă (CRUD + comparare + cascade-delete). |
| Teste | `tests/` | Suita pytest, fixtures comune în `conftest.py`. |

---

## 3. Configurația de execuție

### 3.1 Hardware

| Componentă | Specificație          |
|---|-----------------------|
| CPU | Ryzen 7 9700X         |
| RAM | 32GB RAM DDR5         |
| Stocare | 2TB SSD NVMe PCIe 4.0 |
| Tip sistem | x86_64                |

### 3.2 Software

| Element | Valoare |
|---|---|
| Sistem de operare | Windows 11 Pro (build 10.0.26200) |
| Shell | bash (Git Bash / MINGW64) și PowerShell |
| IDE | PyCharm |
| Limbaj | Python 3.13.2 |
| Mediu izolat | `venv` standard Python (folder `.venv/`) |

### 3.3 Versiuni tool-uri

Snapshot din `pip freeze` la momentul predării 1/3:

| Pachet | Versiune | Rol |
|---|---|---|
| `python` | 3.13.2 | Runtime |
| `pytest` | 9.0.2 | Framework de testare unitară |
| `pluggy` | 1.6.0 | Sistem de plug-in folosit de pytest |
| `iniconfig` | 2.3.0 | Parser pentru `pytest.ini` |
| `Pygments` | 2.20.0 | Colorare sintactică în output-ul pytest |
| `colorama` | 0.4.6 | Suport ANSI pe terminal Windows |
| `packaging` | 26.0 | Comparare versiuni |
| `coverage` | 7.13.5 | Măsurare statement & branch coverage (etapa 2/3) |
| `mutmut` | 2.4.5 | Generator de mutanți pentru mutation testing (etapa 3/3) |

### 3.4 Mașină virtuală

**Nu** s-a folosit mașină virtuală. Codul și testele rulează direct pe sistemul de operare gazdă, izolarea se face exclusiv la nivel de pachete prin `venv`.

---

## 4. Strategii de testare aplicate

### 4.1 Partiționare în clase de echivalență (EC) [1, §4]

**Definiție.** Domeniul fiecărei intrări este împărțit în submulțimi ("clase de echivalență") astfel încât, dacă funcția se comportă corect pentru un reprezentant al clasei, se presupune (cu o probabilitate ridicată) că se comportă corect pentru toți membrii clasei. Fiecare clasă este fie *validă* (input acceptat), fie *invalidă* (input respins, de obicei cu excepție).

**Beneficiu.** Reduce drastic numărul de teste necesare: în loc să testăm toate valorile posibile, testăm un singur reprezentant per clasă.

**Cum am aplicat-o în proiect.** Pentru fiecare parametru al fiecărei funcții/metode testate, am identificat:
- clasele *invalide* (declanșează excepții personalizate),
- clasele *valide* (sunt acceptate și produc o valoare de ieșire).

Exemplu (constructor `TransportPlan`, parametrul `cost_per_km`):
- EC4 *invalid*: `cost_per_km < 0` → `NegativeCostError`
- EC5 *valid*: `cost_per_km >= 0`

### 4.2 Analiza valorilor de frontieră (BVA) [1, §4]

**Definiție.** Defectele apar mai frecvent la marginile partițiilor (operatori `<` vs `<=`, off-by-one). BVA testează exact valorile de pe frontieră și valorile imediat alăturate.

**Beneficiu.** Prinde defecte de tip "off-by-one" și confuzii între operatori relaționali (`<` vs `<=`, `>` vs `>=`).

**Cum am aplicat-o.** La fiecare prag identificat, am scris cazuri de test pentru:
- valoarea exact pe frontieră (verifică condiția `<=` vs `<`),
- valoarea imediat sub (cu un `eps = 0.01`),
- valoarea imediat deasupra.

Exemplu (`weight_surcharge`, prag `ratio = 0.5`):
- `ratio = 0.5` exact → 25% (clasa EC11)
- `ratio = 0.5 + 0.01` → 10% (clasa EC12)

Combinația EC + BVA generează o suită robustă cu redundanță minimă.

---

## 5. Subiecții testați

### 5.1 `Cargo` (constructor)

Reprezintă o marfă: nume, greutate, flag-uri `is_hazardous` / `is_fragile`.

| Parametru | EC valid | EC invalid | Frontieră |
|---|---|---|---|
| `weight` | `>= 0` | `< 0` → `NegativeWeightError` | `weight = 0`, `-0.01` |
| `is_hazardous`, `is_fragile` | `True` / `False` | n/a | n/a |

### 5.2 `FreightTrain` (constructor)

| Parametru | EC valid | EC invalid | Frontieră |
|---|---|---|---|
| `max_capacity` | `> 0` strict | `<= 0` → `InvalidCapacityError` | `0.01`, `0`, `-0.01` |
| `base_speed` | `> 0` strict | `<= 0` → `InvalidSpeedError` | `0.01`, `0`, `-0.01` |

### 5.3 `Route` (constructor)

| Parametru | EC valid | EC invalid | Frontieră |
|---|---|---|---|
| `distance` | `>= 0` | `< 0` → `NegativeDistanceError` | `0`, `-0.01` |
| `difficulty_factor` | `[1.0, 3.0]` | `< 1.0` sau `> 3.0` → `InvalidDifficultyFactorError` | `1.0`, `0.99`, `3.0`, `3.01` |

Conține **prima condiție compusă** testată în proiect: `difficulty_factor < 1.0 or difficulty_factor > 3.0`.

### 5.4 `TransportPlan` (constructor + metode)

Clasa centrală. Constructor cu **5 parametri**, validări multiple, metode de calcul care folosesc partiționări proprii.

**Constructor:** vezi `cargo_list`, `cost_per_km`, `delay`.

**Metode partiționate:**
- `weight_surcharge()`: 3 benzi pe `ratio = total_weight / capacity` (≤ 0.5, (0.5, 0.8], > 0.8).
- `delay_penalty()`: 4 benzi pe `delay` (= 0, (0, 2], (2, 6], > 6).
- `estimated_duration()`: 3 cazuri pe combinația flag-urilor cargo (niciun flag, doar unul, ambele).

În total **16 clase de echivalență** identificate (EC1-EC16) plus frontierele aferente.

### 5.5 `RiskEvaluator.evaluate_shipment_risk` (SUT principal)

Metodă a clasei `RiskEvaluator` din `service/risk_evaluator.py`. Adăugată ca **subiect principal de testare** care satisface, în mod natural, **toate cele 6 criterii** impuse pentru SUT, plus cerința T1 *"testați funcționalitățile unei clase"*:

> *Cerință profesor:* funcția trebuie să aibă **min. 3 parametri**, să conțină **cel puțin o instrucțiune repetitivă**, **2 condiționale (un `if` cu `else` și altul fără `else`)**, **o condiție simplă** și **una compusă**.

**Verificarea criteriilor:**

| Criteriu | Element în cod |
|---|---|
| ≥ 3 parametri | `cargo_list, train, route, delay_hours` (4 parametri) |
| ≥ 1 instrucțiune repetitivă | `for c in cargo_list:` |
| `if` cu `else` | `if route.difficulty_factor >= 2.0 and delay_hours > 4: ... else: ...` |
| `if` fără `else` | `if c.is_hazardous: ...`, `if hazardous_weight > 0 and ratio > 0.7: return "HIGH"` |
| Condiție simplă | `c.is_hazardous`, `delay_hours < 0`, `ratio > 0.5` |
| Condiție compusă | `hazardous_weight > 0 and ratio > 0.7`, `route.difficulty_factor >= 2.0 and delay_hours > 4` |

**Specificație.** Funcția returnează nivelul de risc al unui transport, ca string: `"LOW"`, `"MEDIUM"` sau `"HIGH"`. Reguli:

1. Dacă transportul conține mărfuri periculoase **și** trenul este aproape plin (`ratio > 0.7`) → `"HIGH"`.
2. Dacă ruta este dificilă (`difficulty_factor >= 2.0`) **și** întârzierea este mare (`> 4` ore) → `"HIGH"`.
3. Altfel, dacă `ratio > 0.5` → `"MEDIUM"`.
4. Altfel → `"LOW"`.

**Validări.** `delay_hours < 0` → `NegativeDelayError`. Listă goală → `EmptyCargoListError`.

---

## 6. Diagrame

> Toate diagramele au fost realizate în [draw.io](https://app.diagrams.net/) (denumit oficial diagrams.net), tool dedicat din lista acceptată în cerințele temei. Exporturile PNG sunt incluse mai jos, iar sursele `.drawio` editabile pot fi adăugate în folderul `Diagrame/` pentru auditare.

### 6.1 Diagrama de clase - stratul de domeniu

![Diagrama de clase pentru stratul domain](<Diagrame/diagrama domeniu.png>)

*Diagrama prezintă cele 4 entități din `domain/` și relațiile dintre ele: `TransportPlan` agregă un `FreightTrain` și un `Route` (romb gol — uses, lifetime decuplat) și conține o listă de `Cargo` (1..N).*

### 6.2 Diagrama de flux pentru `evaluate_shipment_risk`

Reprezintă fluxul de decizie complet al SUT-ului: cele două validări care pot declanșa excepții, loop-ul de calcul al greutății totale și al greutății de marfă periculoasă, apoi cele 3 reguli succesive de clasificare a riscului.

![Flowchart pentru evaluate_shipment_risk](<Diagrame/Flowchart pentru evaluate_shipment_risk.png>)

*Cele două ramuri „HIGH" (regulile 1 și 2) marchează ieșiri timpurii ale funcției. Ramura else din `if difficulty >= 2.0 and delay > 4` continuă cu testul `ratio > 0.5` care decide între MEDIUM și LOW.*

### 6.3 Diagrama suprapunerilor EC + BVA pe `weight_surcharge` (TransportPlan)

![Partitionare EC + BVA pe axa raportului weight/capacity](<Diagrame/Partiționare EC + BVA pentru weight_surcharge.png>)

*Cele 3 clase de echivalență (EC11, EC12, EC13) acoperă întreg domeniul `ratio = total_weight / max_capacity`. Punctele BVA marcate sub axă verifică direct operatorii relaționali: `0.5` și `0.5+ε` separă EC11 de EC12, iar `0.8` și `0.8+ε` separă EC12 de EC13.*

---

## 7. Bucăți de cod relevante

### 7.1 SUT-ul principal: `RiskEvaluator.evaluate_shipment_risk`

Fișier: `service/risk_evaluator.py`

```python
from exceptions.transport_exceptions import NegativeDelayError, EmptyCargoListError


class RiskEvaluator:

    def evaluate_shipment_risk(self, cargo_list, train, route, delay_hours):
        # validari
        if delay_hours < 0:
            raise NegativeDelayError("Intarzierea nu poate fi negativa: " + str(delay_hours))
        if not cargo_list:
            raise EmptyCargoListError("Lista de marfuri nu poate fi goala")

        # calculez greutatea totala si greutatea marfurilor periculoase
        total_weight = 0
        hazardous_weight = 0
        for c in cargo_list:
            total_weight = total_weight + c.weight
            if c.is_hazardous:
                hazardous_weight = hazardous_weight + c.weight

        # raportul greutate / capacitate
        ratio = total_weight / train.max_capacity

        # marfa periculoasa + tren aproape plin => risc maxim
        if hazardous_weight > 0 and ratio > 0.7:
            return "HIGH"

        # ruta dificila + intarziere mare => risc maxim
        if route.difficulty_factor >= 2.0 and delay_hours > 4:
            risk = "HIGH"
        else:
            if ratio > 0.5:
                risk = "MEDIUM"
            else:
                risk = "LOW"

        return risk
```

Folosire în teste: `RiskEvaluator().evaluate_shipment_risk(cargo_list, train, route, delay_hours)`.

### 7.2 Exemplu de test EC: `TransportPlan` capacitate

Fișier: `tests/test_transport_plan_blackbox.py`

```python
def test_ec3_total_weight_exceeds_capacity_raises(train_100t_80kmh, route_450_diff1):
    """EC3: total_weight > capacitate."""
    with pytest.raises(CapacityExceededError):
        TransportPlan(
            train_100t_80kmh, route_450_diff1,
            [Cargo("M", 60.0), Cargo("N", 50.0)], cost_per_km=5.0,
        )
```

### 7.3 Exemplu de test BVA: frontiera la prag

```python
def test_bva_total_weight_just_above_capacity_raises(train_100t_80kmh, route_450_diff1):
    """Frontiera: total = capacitate + eps => CapacityExceededError."""
    with pytest.raises(CapacityExceededError):
        TransportPlan(
            train_100t_80kmh, route_450_diff1,
            [Cargo("M", 100.01)], cost_per_km=5.0,
        )
```

### 7.4 Exemplu de test parametrizat (compactare BVA pe set de valori)

```python
@pytest.mark.parametrize("delay", [-0.01, -1, -100])
def test_ec3_delay_negative_raises(
    train_100t_80kmh, route_450_diff1, cargo_normal, delay
):
    """EC3: delay_hours < 0 => NegativeDelayError."""
    with pytest.raises(NegativeDelayError):
        RiskEvaluator().evaluate_shipment_risk([cargo_normal], train_100t_80kmh, route_450_diff1, delay)
```

### 7.5 Fixtures comune (`tests/conftest.py`)

```python
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
```

---

## 8. Rezultate experimentale

### 8.1 Rulare suita completă

Comandă:

```bash
.venv/Scripts/python -m pytest tests/ -v
```

**Rezumat numeric:**

```
============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Users\rober\PycharmProjects\Proiect_TSS_v2
configfile: pytest.ini
collected 164 items

........................................................................ [ 87%]
....................                                                     [100%]

============================= 164 passed in 0.13s ==============================
```

**Captură de ecran cu rularea `pytest -v`:**

![Output pytest -v cu toate testele PASSED](<screenshots/pytest -v.png>)

**Captură de ecran cu colectarea (`pytest --collect-only -q`):**

![Lista testelor colectate, util pentru auditul EC/BVA](<screenshots/pytest --collect-only -q.png>)

### 8.2 Distribuția testelor pe fișiere

| Fișier | Subiectul testat | Nr. teste | Strategii |
|---|---|---|---|
| `tests/test_cargo_blackbox.py` | `Cargo.__init__` + `__repr__` | 10 | EC + BVA |
| `tests/test_freight_train_blackbox.py` | `FreightTrain.__init__` | 20 | EC + BVA |
| `tests/test_route_blackbox.py` | `Route.__init__` | 27 | EC + BVA (incl. condiție compusă) |
| `tests/test_transport_plan_blackbox.py` | `TransportPlan.__init__` + 3 metode | 45 | EC + BVA |
| `tests/test_risk_evaluator_blackbox.py` | `RiskEvaluator.evaluate_shipment_risk` (SUT principal) | 23 | EC + BVA |
| `tests/test_risk_evaluator_whitebox.py` | `RiskEvaluator.evaluate_shipment_risk` (SUT principal) | 36 | Statement / Branch / Condition / Independent paths |
| `tests/test_risk_evaluator_mutation.py` | `RiskEvaluator.evaluate_shipment_risk` (SUT principal) | 3 | Teste suplimentare pentru kill mutanți |
| **Total** | | **164** | |

### 8.3 Distribuția claselor de echivalență

Identificate pentru fiecare subiect (numerotate global EC1-EC16 pentru `TransportPlan`, plus EC1-EC8 dedicate pentru `evaluate_shipment_risk`):

| Subiect | EC valide | EC invalide | Total EC |
|---|---|---|---|
| `Cargo.__init__` | 1 (`weight >= 0`) | 1 (`< 0`) | 2 |
| `FreightTrain.__init__` | 2 (`capacity > 0`, `speed > 0`) | 2 | 4 |
| `Route.__init__` | 1 (`distance >= 0`) + 1 (`factor in [1, 3]`) | 1 + 1 | 4 |
| `TransportPlan` (constructor + metode) | 8 (EC2, EC5, EC7-10, EC11-13, EC14-16) | 4 (EC1, EC3, EC4, EC6) | 16 |
| `evaluate_shipment_risk` | 4 (EC2 valid, EC4 valid, EC5-8 ieșiri) | 2 (EC1, EC3) | 8 |

### 8.4 Frontiere BVA testate

Total: **22 de puncte de frontieră distincte** testate cu valori `frontieră`, `frontieră ± ε`.

| Subiect | Frontiere |
|---|---|
| `Cargo` | `weight = 0`, `-0.01` |
| `FreightTrain` | `capacity = 0`, `0.01`, `-0.01`; `speed = 0`, `0.01`, `-0.01` |
| `Route` | `distance = 0`, `-0.01`; `factor = 1.0`, `0.99`, `3.0`, `3.01` |
| `TransportPlan` | `total = capacity` (±ε); `cost = 0` (±ε); `delay = 0`, `2`, `6` (±ε); `ratio = 0.5`, `0.8` (±ε) |
| `evaluate_shipment_risk` | `delay = 0` (±ε); `ratio = 0.5`, `0.7` (±ε); `difficulty = 2.0` (±ε); `delay = 4` (±ε) |

---

## 9. Comparații tabelare

### 9.1 EC vs BVA: rolul fiecărei strategii

| Aspect | Partiționare EC | Analiza valorilor de frontieră (BVA) |
|---|---|---|
| Întrebarea pusă | "Ce categorii distincte de input există?" | "Ce se întâmplă exact pe marginile categoriilor?" |
| Tipul defectelor prinse | Logica de afaceri greșită pe o întreagă clasă (ex: tratează negativele ca pozitive) | Off-by-one, confuzie `<` vs `<=`, comparații incorecte |
| Număr cazuri | 1 per clasă (reprezentant) | 2-3 per frontieră |
| Atomic sau redundant cu EC? | Atomic | Suprapunere parțială (valoarea de pe frontieră aparține unei EC) |
| Exemplu prinzător în proiectul nostru | EC11 vs EC12 (suprataxe diferite la rate diferite) | `ratio = 0.5` (verifică `<= 0.5`, nu `< 0.5`) |

### 9.2 Distribuția efortului pe strategii (SUT principal)

Pentru `evaluate_shipment_risk` (23 teste totale):

| Categorie | Nr. teste | % |
|---|---|---|
| EC valide (output corect) | 7 | 30% |
| EC invalide (excepții) | 4 | 17% |
| BVA pe praguri | 9 | 39% |
| Cazuri de defensivă (combinații) | 3 | 13% |

Ponderea ridicată a BVA reflectă numărul de praguri numerice din specificație (4 praguri: 0.5, 0.7, 2.0, 4.0).

### 9.3 Volum cod sursă vs cod test

| Componentă | Linii sursă (LOC) | Linii test |
|---|---|---|
| `domain/` (4 clase) | ~95 | ~190 |
| `service/risk_evaluator.py` | 38 | ~510 (BB + WB + mutation pe SUT) |
| **Total cod testat** | ~133 LOC sursă | ~700 LOC test |

Raportul **test:cod ≈ 5:1** este în concordanță cu recomandările pentru aplicații cu reguli de afaceri [3, cap. 4]; raport mai mare reflectă acoperirea adăugată de WB și mutation pe SUT.

---

## 10. Interpretarea rezultatelor

**1. Acoperire la nivel de specificație.** Cele 125 de teste BB (10 + 20 + 27 + 45 + 23) acoperă fiecare clasă de echivalență identificată (24 EC totale) și fiecare frontieră numerică (22 puncte). Nu am identificat nicio EC fără cel puțin un caz de test corespondent. Restul de 39 teste (36 WB + 3 mutation) sunt pentru etapele 2/3 și 3/3, descrise în PARTEA A II-A și A III-A.

**2. Validarea independenței validărilor.** Ordinea în care `TransportPlan.__init__` verifică inputurile (lista vidă → cost negativ → delay negativ → capacitate depășită) este testată implicit: pentru fiecare excepție am verificat că *exact* acea excepție este aruncată (nu un mesaj generic), folosind `pytest.raises(SpecificError)`.

**3. Decizii de design rezultate din scrierea testelor.** În timpul scrierii testelor BVA pentru `weight_surcharge`, am decis că pragul `0.5` este *inclus* în EC11 (`<= 0.5`), nu în EC12. Această decizie este reflectată direct în cod (`if ratio <= 0.5:`) și verificată prin `test_bva_surcharge_ratio_exactly_0_5`.

**4. Fixture-uri ca reducere de zgomot.** Cele 3 fixture-uri din `conftest.py` (`train_100t_80kmh`, `route_450_diff1`, `cargo_normal`) sunt reutilizate în toate fișierele de test. Aceasta a redus dimensiunea testelor cu ~25% și a făcut intenția fiecărui test mai vizibilă (testul izolează *un* parametru variabil într-un context fixat).

**5. Limitele black-box-ului.** Testele actuale nu garantează acoperire structurală a codului. De exemplu, ramificația `else` din `weight_surcharge` (`return 0.0` când `ratio > 0.8`) este executată, dar nu am verificat dacă fiecare ramificație din interpretorul condiției compuse `cost_per_km < 0 or delay < 0` ar fi acoperită toate combinațiile - aceasta este o sarcină pentru etapa 2/3 (white-box).

**6. Robustețe la mărirea volumului de date.** Testul `test_loop_iterates_through_all_cargo_items` verifică că metoda `RiskEvaluator.evaluate_shipment_risk` procesează corect liste de mărimi diferite (1, 2, 3 elemente). Nu am testat liste mari (>1000) deoarece logica este O(n) liniară fără efecte secundare - nu există motiv structural ca un volum mare să producă defecte noi (afirmație validă în lipsa claselor cu stare ascunsă).

---

## 11. Referințe bibliografice

[1] Aniche, Maurício, *Effective Software Testing: A developer's guide*, Simon and Schuster, 2022.

[2] Khorikov, Vladimir, *Unit Testing Principles, Practices, and Patterns*, Simon and Schuster, 2020.

[3] Pytest Development Team, *pytest documentation*, https://docs.pytest.org/.

[4] Python Software Foundation, *Python 3.13 Language Reference*, https://docs.python.org/3.13/reference/.

[5] Predut, Sorina-Nicoleta, *Curs Testarea Sistemelor Software — Functional Testing, Structural Testing, Mutation Testing*, Material de curs FMI, 2024-2026.

[6] ISTQB, *Foundation Level Syllabus v4.0*, International Software Testing Qualifications Board, 2023, https://www.istqb.org/.

[7] Batchelder, Ned, *Coverage.py — code coverage tool for Python*, https://coverage.readthedocs.io/.

[8] Boxed, Anders, *mutmut — mutation testing for Python*, https://mutmut.readthedocs.io/.

[9] McCabe, Thomas J., *A Complexity Measure*, IEEE Transactions on Software Engineering, vol. SE-2, no. 4, 1976, pp. 308-320.

[10] DeMillo, Lipton, Sayward, *Hints on test data selection: Help for the practicing programmer*, IEEE Computer, vol. 11, no. 4, 1978, pp. 34-41. (Originatorii tehnicii de mutation testing.)

---

# PARTEA A II-A: Testare structurală (white-box) — Etapa 2/3

## 12. Strategii structurale aplicate

Spre deosebire de testele black-box (care derivă cazurile din specificație, ignorând codul intern), testele white-box sunt construite **pe baza implementării** [Curs §2 — Structural Testing]. SUT-ul rămâne același — metoda `RiskEvaluator.evaluate_shipment_risk` din `service/risk_evaluator.py` — dar cazurile de test sunt acum aliniate la structura codului ei (CFG).

### 12.1 Statement coverage (acoperire la nivel de instrucțiune)

**Definiție.** Fiecare instrucțiune executabilă din SUT trebuie să fie parcursă de cel puțin un test [Curs §2(a)].

**Beneficiu.** Asigură că nicio linie de cod nu este complet netestată; este nivelul minim de acoperire structurală.

**Limite.** Nu testează fiecare ramură (un `if` fără `else` poate avea statement coverage 100% chiar dacă ramura `False` nu este niciodată exersată) și nu testează sub-condițiile compuse independent.

### 12.2 Decision/Branch coverage (acoperire la nivel de decizie)

**Definiție.** Fiecare ramură (T sau F) a fiecărei decizii din CFG este executată cel puțin o dată [Curs §2(b)].

**Beneficiu.** Extindere naturală a statement coverage. Forțează exersarea ramurilor `else` implicite (când `if` nu are `else`, ramura `False` este "skip"-ul peste corpul `if`).

**Limite.** Pentru condiții compuse (`a and b`, `a or b`), branch coverage poate fi obținut fără a testa fiecare sub-condiție atomică independent.

### 12.3 Condition coverage (acoperire la nivel de condiție)

**Definiție.** Fiecare condiție atomică dintr-o decizie compusă trebuie să ia atât valoarea `True` cât și `False`, independent de celelalte sub-condiții [Curs §2(c)].

**Beneficiu.** Forțează scrierea de teste care pun în evidență fiecare sub-condiție din expresii `and`/`or` — important pentru a prinde defecte de tip operator greșit (`and` ↔ `or`) sau sub-condiție lipsă.

### 12.4 Circuite independente — complexitate ciclomatică McCabe

**Definiție.** Numărul de căi linear independente prin CFG [Curs §2(g)]. Calculat cu formula McCabe:

```
V(G) = e − n + 2p
```

unde `e` = numărul de muchii, `n` = numărul de noduri, `p` = numărul de componente conexe (= 1 pentru o singură funcție/subprogram).

Formulă echivalentă, mai simplă pentru un singur subprogram:

```
V(G) = #decizii + 1
```

**Beneficiu.** Identifică limita superioară pentru numărul de căi necesare pentru acoperirea la nivel de ramură. Setul de căi independente este o "bază" — orice altă cale prin CFG este o combinație liniară a celor V(G) căi.

---

## 13. CFG pentru `evaluate_shipment_risk`

### 13.1 Structura grafului

CFG-ul a fost construit pe baza codului SUT (vezi §7.1 sau `service/risk_evaluator.py`) după regulile din [Curs §2]:
- secvență de instrucțiuni → un nod
- `if c then s1 else s2` → nod `c` cu două muchii la `s1`, `s2`, ambele converg la `ex`
- `for c do s` (ca `while`) → nod-condiție cu back-edge

Rezultat: **n = 19 noduri, e = 25 muchii** (incluzând nodul virtual `EXIT`).

### 13.2 Punctele de decizie

| Eticheta | Cod | Tip | Linii sursă |
|---|---|---|---|
| D1 | `if delay_hours < 0` | simplă | 8 |
| D2 | `if not cargo_list` | simplă | 10 |
| D_loop | `for c in cargo_list` (implicit `hasNext`) | simplă | 16 |
| D3 | `if c.is_hazardous` | simplă | 18 |
| D4 | `if hazardous_weight > 0 and ratio > 0.7` | **compusă** | 25 |
| D5 | `if route.difficulty_factor >= 2.0 and delay_hours > 4` | **compusă (cu `else`)** | 29 |
| D6 | `if ratio > 0.5` | simplă | 32 |

**7 decizii** ⇒ V(G) = 7 + 1 = **8** (formulă simplificată).

Verificare cu formula generală: V(G) = e − n + 2 = 25 − 19 + 2 = **8** ✓.

### 13.3 Diagrama CFG

![CFG pentru evaluate_shipment_risk](<Diagrame/cfg_evaluate_shipment_risk.png>)

*Diagrama prezintă fluxul de control complet: două validări inițiale care pot termina cu excepție (linii roșii întrerupte spre `EXIT`), bucla peste `cargo_list` cu back-edges spre `D_loop`, și cele 3 reguli succesive (D4, D5, D6) care decid riscul. Nodul virtual `EXIT` agregă toate ieșirile (prin `return` sau `raise`).*

---

## 14. Statement coverage — mapare teste

Cele 22 de instrucțiuni executabile ale SUT-ului (incluzând declarația de clasă) sunt acoperite de testele din `tests/test_risk_evaluator_whitebox.py`, secțiunea 1:

| Test | Instrucțiuni acoperite |
|---|---|
| `test_stmt_validation_negative_delay` | D1=T, raise `NegativeDelayError` |
| `test_stmt_validation_empty_cargo` | D1=F, D2=T, raise `EmptyCargoListError` |
| `test_stmt_full_path_low` | init weights, loop body fără haz, ratio compute, D4=F, D5=F, D6=F, return `"LOW"` |
| `test_stmt_hazardous_assignment` | D3=T, `hazardous_weight += c.weight` |
| `test_stmt_high_rule_1` | D4=T, return `"HIGH"` (rule 1) |
| `test_stmt_high_rule_2` | D5=T, `risk = "HIGH"` (rule 2) |
| `test_stmt_medium` | D6=T, `risk = "MEDIUM"` |

**Rezultat măsurat de tool-ul `coverage`**: **22/22 statements (100%)**.

---

## 15. Decision/Branch coverage — mapare teste

7 decizii × 2 ramuri = **14 ramuri** de acoperit. Mapare:

| Decizie | Ramura T (test) | Ramura F (test) |
|---|---|---|
| D1 | `test_branch_d1_true` | `test_branch_d1_false` |
| D2 | `test_branch_d2_true` | `test_branch_d2_false` |
| D_loop | `test_branch_loop_iterates` (T și F implicit într-un singur test cu listă nevidă) | (același) |
| D3 | `test_branch_d3_true` | `test_branch_d3_false` |
| D4 | `test_branch_d4_true` | `test_branch_d4_false` |
| D5 | `test_branch_d5_true` | `test_branch_d5_false` |
| D6 | `test_branch_d6_true` | `test_branch_d6_false` |

**Rezultat măsurat**: **14/14 ramuri (100%)** cu flag-ul `--branch` al tool-ului `coverage`.

---

## 16. Condition coverage — sub-condiții atomice

Cele 2 decizii compuse au câte 2 sub-condiții atomice. Pentru condition coverage, fiecare sub-condiție trebuie să ia atât T cât și F. Acoperim toate cele 4 combinații (echivalent multiple condition coverage pentru aceste decizii):

### 16.1 D4 = (`hazardous_weight > 0`) ∧ (`ratio > 0.7`)

| Test | C1 (haz>0) | C2 (ratio>0.7) | D4 | Rezultat |
|---|---|---|---|---|
| `test_cond_d4_haz_T_ratio_T` | T | T | T | "HIGH" |
| `test_cond_d4_haz_T_ratio_F` | T | F | F | "LOW" |
| `test_cond_d4_haz_F_ratio_T` | F | T | F | "MEDIUM" |
| `test_cond_d4_haz_F_ratio_F` | F | F | F | "LOW" |

C1 ia T în testele 1, 2 și F în testele 3, 4. C2 ia T în testele 1, 3 și F în 2, 4.

### 16.2 D5 = (`difficulty_factor >= 2.0`) ∧ (`delay_hours > 4`)

| Test | C1 (diff≥2.0) | C2 (delay>4) | D5 | Rezultat |
|---|---|---|---|---|
| `test_cond_d5_diff_T_delay_T` | T | T | T | "HIGH" |
| `test_cond_d5_diff_T_delay_F` | T | F | F | "LOW" |
| `test_cond_d5_diff_F_delay_T` | F | T | F | "LOW" |
| `test_cond_d5_diff_F_delay_F` | F | F | F | "LOW" |

C1 ia T în testele 1, 2 și F în 3, 4. C2 ia T în 1, 3 și F în 2, 4.

**Total**: 8 teste × 2 sub-condiții × 2 valori → condition coverage 100% pe ambele decizii compuse.

---

## 17. Circuite independente (McCabe) — set de bază

Cele V(G) = **8 căi linear independente**. Fiecare cale = o combinație unică de decizii cu un test asociat în `tests/test_risk_evaluator_whitebox.py`, secțiunea 4.

| # | Cale | Decizii cheie | Test | Rezultat |
|---|------|---------------|------|----------|
| P1 | START → D1=T → raise → EXIT | D1=T | `test_path_1_d1_true` | excepție `NegativeDelayError` |
| P2 | START → D1=F → D2=T → raise → EXIT | D2=T | `test_path_2_d2_true` | excepție `EmptyCargoListError` |
| P3 | … D2=F → init → loop=1iter no-haz → D4=F → D5=T → "HIGH" | D5=T | `test_path_3_high_rule_2` | "HIGH" (rule 2) |
| P4 | … D5=F → D6=T → "MEDIUM" | D6=T | `test_path_4_medium` | "MEDIUM" |
| P5 | … D5=F → D6=F → "LOW" | D6=F | `test_path_5_low` | "LOW" |
| P6 | … loop=1iter haz → D4=T → "HIGH" | D3=T, D4=T | `test_path_6_high_rule_1` | "HIGH" (rule 1) |
| P7 | … loop=1iter haz → D4=F → D5=F → D6=F → "LOW" | D3=T, D4=F | `test_path_7_haz_low_ratio` | "LOW" |
| P8 | … loop=2+ iter (mix) | D_loop iterează ≥ 2 ori | `test_path_8_loop_multiple_iterations` | "MEDIUM" |

Fiecare test exercită cel puțin o muchie sau un nod neexersat de testele anterioare, garantând independența liniară a căilor.

---

## 18. Rezultate coverage tool

### 18.1 Comenzi rulate

```bash
.venv/Scripts/python -m coverage erase
.venv/Scripts/python -m coverage run --branch --source=service.risk_evaluator -m pytest tests/test_risk_evaluator_blackbox.py tests/test_risk_evaluator_whitebox.py
.venv/Scripts/python -m coverage report -m
.venv/Scripts/python -m coverage html -i
```

### 18.2 Output text (`coverage report`)

```
Name                        Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------
service\risk_evaluator.py      22      0     14      0   100%
-------------------------------------------------------------
TOTAL                          22      0     14      0   100%
```

### 18.3 Raport HTML

**Captură de ecran cu raportul HTML** (`htmlcov/index.html` deschis în browser):

![Raport HTML coverage 100% pe risk_evaluator.py](<screenshots/coverage html report.png>)

**Captură de ecran cu output-ul terminalului** (`coverage report -m`):

![Output terminal coverage report](<screenshots/coverage terminal output.png>)

### 18.4 Observație onestă

Suita black-box (23 teste, §1-§11) atinge deja 100% statement și 100% branch coverage pe `evaluate_shipment_risk`. Suita white-box (36 teste, §12-§17) **nu îmbunătățește scorul de coverage**, dar îndeplinește alte cerințe importante:

1. **Ilustrare explicită a strategiilor** (§14-§17) — cerința T1: *"ilustrați strategiile de generare de teste prezentate la curs"*.
2. **Documentare a circuitelor independente** — cerință explicită din `teme_proiect_TSS.pdf` ("acoperire la nivel de circuite independente").
3. **Condition coverage explicit** pe sub-condițiile atomice ale celor două decizii compuse — care nu este garantat de simpla branch coverage.

Această observație este importantă: **100% coverage ≠ teste bune sau cod corect** [Curs Coverage Testing §10] — exemplul `isPrime` din PDF-ul cursului arată că 100% statement coverage poate ascunde defecte (funcția returna False pentru input=2 chiar și cu acoperire totală). Mutation testing (etapa 3/3) va verifica robustețea reală a suitei.

---

## 19. Interpretarea rezultatelor white-box

**1. Codul SUT este suficient de structurat pentru a permite acoperire 100%.** Cele 21 de instrucțiuni și 14 ramuri sunt toate fezabile (nu există cod mort, nu există ramuri infezabile care ar necesita marcaj `# pragma: no cover`).

**2. Black-box-ul a fost suficient de complet la nivel structural.** Cele 23 de teste BB ating deja 100% — sugerează că EC + BVA aplicate sistematic peste fiecare parametru produc o suită cu acoperire structurală bună. Nu este o regulă generală, dar pentru SUT-ul nostru (logică de afaceri pură, fără efecte secundare) funcționează.

**3. Condition coverage adaugă valoare reală.** Branch coverage e satisfăcută de 2 teste pe D4 (T și F), dar condition coverage cere 4 (toate combinațiile sub-condițiilor). Aceste 4 combinații vor fi cele care prind cei mai mulți mutanți pe operatorii logici (`and` ↔ `or`), în etapa 3/3.

**4. Bucla `for` este testată cu 1 → ≥2 iterații.** Cazul "0 iterații" este blocat structural (D2 raise pentru listă goală), deci nu este aplicabil. Restul scenariilor sunt acoperite — îndeplinește criteriul informal de "loop coverage" [Curs Coverage Testing §16].

**5. Complexitatea ciclomatică V(G) = 8 este moderată.** Conform recomandărilor uzuale (V(G) ≤ 10 pentru o funcție ușor de înțeles), funcția se află în zona de "complexitate acceptabilă". Dacă V(G) ar depăși 15-20, ar fi un semnal că funcția trebuie refactorizată. Cele 8 căi independente sunt toate fezabile și au teste asociate.

**6. Limitele acoperirii structurale rămân.** Coverage-ul nu detectează *erori de omisiune* (lipsa unei verificări) și nu garantează că logica de afaceri este corectă. Etapa 3/3 (mutation testing) completează această evaluare prin generarea sistematică de mutanți și verificarea capacității suitei de a-i distinge.

---

# PARTEA A III-A: Mutation testing — Etapa 3/3

## 20. Strategie: mutation testing

### 20.1 Definiție și principii

**Mutation testing** este o tehnică de evaluare a unui set de teste prin generarea unor variante ușor modificate ale codului sursă (numite *mutanți*) și verificarea cât de eficient suita existentă distinge mutanții de codul original [Curs Mutation Testing §1].

Pentru un program `P`, un **mutant** `M` este un program obținut din `P` prin aplicarea unei singure modificări sintactice (operator de mutație). Pentru fiecare test `t` din suită:

- dacă `P(t) ≠ M(t)` ⇒ testul `t` **omoară** mutantul `M`;
- dacă pentru toate testele `P(t) == M(t)` ⇒ mutantul **supraviețuiește**.

Pentru ca un test să omoare un mutant, trebuie să îndeplinească 3 condiții [Curs §, "Detectarea erorilor folosind mutația"]:
1. **Reachability**: instrucțiunea mutată trebuie să fie executată.
2. **State infection**: instrucțiunea mutată trebuie să afecteze starea programului.
3. **State propagation**: schimbarea de stare trebuie să se propage la ieșirea observabilă.

### 20.2 Mutanți echivalenți

Un mutant `M` se numește **echivalent** dacă pentru *orice* date de intrare se comportă identic cu `P`. Determinarea echivalenței este în general nedecidabilă (echivalentă cu *halting problem*) [Curs §, "Mutanți echivalenți"]; în practică se face prin inspecție vizuală a codului mutat.

### 20.3 Mutation score

Definit formal:

```
MS(T) = D / (L + D)
```
unde:
- `D` = numărul de mutanți distinși (omorâți)
- `L` = numărul de mutanți supraviețuitori **NEechivalenți**

Mutanții echivalenți NU intră în calcul (sunt eliminați din numitor).

### 20.4 Cerința proiectului T1

Conform `teme_proiect_TSS.pdf`:

> *"analiză raport creat de generatorul de mutanți, **teste suplimentare pentru a omorî 2 dintre mutanții neechivalenți rămași în viață** pe exemple proprii"*

Adică: după rularea suitei BB+WB, identificăm mutanții supraviețuitori și scriem **min. 2 teste suplimentare** care să omoare 2 dintre ei (clasificați ca non-echivalenți).

---

## 21. Tool: `mutmut`

### 21.1 Versiune și particularități

| Tool | Versiune | Observații |
|---|---|---|
| `mutmut` | 2.4.5 | Versiunea 3.x are bug pe Windows native; versiunea 2.5.1 are bug în pony ORM cu Python 3.13 |
| `pony` (dependent) | 0.7.17 | Pinat la 0.7.17 pentru compatibilitate cu Python 3.13 |

Configurat să muteze `service/risk_evaluator.py` și să ruleze testele pe SUT (BB + WB + mutation) ca runner.

### 21.2 Operatorii de mutație folosiți de mutmut

`mutmut` aplică automat operatori clasici la nivel de AST:

| Operator | Exemplu |
|---|---|
| Comparație | `>` ↔ `>=`, `<` ↔ `<=`, `==` ↔ `!=` |
| Constante numerice | `0` → `1`, `0.7` → `1.7` sau `0.71` |
| Constante string | `"text"` → `"XXtextXX"` (prefix/sufix marker) |
| Operatori logici | `and` ↔ `or` |
| Negație | `not x` → `x` |
| Operatori aritmetici | `+` → `-`, `*` → `/` |
| Apel funcție | `func(x)` → `func(None)` |

### 21.3 Comenzi rulate

Mutation testing este un proces în două etape: o **rulare inițială** doar cu testele BB + WB pentru a identifica supraviețuitori, urmată de o **rulare finală** cu testele suplimentare incluse pentru a verifica că supraviețuitorii sunt omorâți.

**A. Rulare INIȚIALĂ** (după BB + WB, înainte de testele suplimentare):

```bash
# Curățare cache (forțează rulare completă)
rm -f .mutmut-cache  # Git Bash; Windows nativ: del .mutmut-cache

PYTHONIOENCODING=utf-8 .venv/Scripts/python -m mutmut run \
    --paths-to-mutate=service/risk_evaluator.py \
    --runner=".venv\Scripts\python.exe -m pytest tests/test_risk_evaluator_blackbox.py tests/test_risk_evaluator_whitebox.py -x -q --no-header"
```

Rezultat așteptat: **32 omorâți / 3 supraviețuitori** (ID-uri #3, #6, #18).

**B. Rulare FINALĂ** (după adăugarea testelor suplimentare):

```bash
# Curățare cache din nou (cache-ul e invalidat de modificarea suitei)
rm -f .mutmut-cache

PYTHONIOENCODING=utf-8 .venv/Scripts/python -m mutmut run \
    --paths-to-mutate=service/risk_evaluator.py \
    --runner=".venv\Scripts\python.exe -m pytest tests/test_risk_evaluator_blackbox.py tests/test_risk_evaluator_whitebox.py tests/test_risk_evaluator_mutation.py -x -q --no-header"
```

Rezultat așteptat: **35 omorâți / 0 supraviețuitori**.

**Comenzi auxiliare** (vizualizare diff și citire cache, valabile pentru ambele rulări):

```bash
# Vizualizare diff per mutant
PYTHONIOENCODING=utf-8 .venv/Scripts/python -m mutmut show <id>

# Citire cache rezultate (workaround pentru bug-ul pony+Python3.13)
.venv/Scripts/python -c "
import sqlite3
con = sqlite3.connect('.mutmut-cache')
for row in con.execute('SELECT status, COUNT(*) FROM Mutant GROUP BY status'):
    print(row)
"
```

---

## 22. Rezultatul rulării inițiale (suita BB + WB)

### 22.1 Statistici

`mutmut` a generat **35 mutanți** pentru `service/risk_evaluator.py`:

| Categorie | Număr | Pondere |
|---|---|---|
| Omorâți (`ok_killed`) | 32 | 91.4% |
| Supraviețuitori (`bad_survived`) | 3 | 8.6% |
| Timeout / suspicious / skipped | 0 | 0% |
| **Total** | **35** | **100%** |

### 22.2 Mutation score inițial

Înainte de a clasifica supraviețuitorii ca echiv/non-echiv, scorul brut este:

```
MS_brut = D / total = 32 / 35 ≈ 91.4%
```

### 22.3 Capturi de ecran (rulare INIȚIALĂ)

**Captură de ecran cu output-ul `mutmut run` — rulare inițială (BB + WB only):**

![Output mutmut rulare inițială - 32 omorâți, 3 supraviețuitori](<screenshots/mutmut_initial_run.png>)

**Captură de ecran cu cache-ul SQLite — rulare inițială:**

![Cache mutmut SQLite - 32 ok_killed, 3 bad_survived](<screenshots/mutmut_initial_sqlite.png>)

---

## 23. Analiza supraviețuitorilor

Folosind `mutmut show <id>`, am extras diff-ul pentru fiecare dintre cei 3 supraviețuitori. Capturi de ecran ale fiecărui diff sunt anexate.

### 23.1 Mutant #3 (linia 9, mesaj `NegativeDelayError`)

```diff
-            raise NegativeDelayError("Intarzierea nu poate fi negativa: " + str(delay_hours))
+            raise NegativeDelayError("XXIntarzierea nu poate fi negativa: XX" + str(delay_hours))
```

![Diff mutant #3](<screenshots/mutmut_show_3.png>)

**De ce a supraviețuit?** Testele BB+WB verifică doar tipul excepției (`pytest.raises(NegativeDelayError)`), nu și textul mesajului. Adăugarea prefixelor/sufixelor `"XX"` lasă logica intactă; doar mesajul afișat se schimbă.

**Clasificare: NON-ECHIVALENT la nivel de contract observabil.**

Argumentul (întărit cu referințe academice):

1. **Definiția "strong mutation"** [Curs Mutation Testing, secțiunea "Strong mutation/weak mutation"]: un test t omoară mutantul M dacă comportamentul observabil al lui P și M diferă pentru t. Mesajul atașat unei excepții este parte a comportamentului observabil — apelantul (`pytest.raises(...) as exc_info`) poate citi `str(exc_info.value)`, deci mesajul ESTE observabil.
2. **Standardul IEEE 829-2008** (Test Documentation), §8.2.2: textul mesajelor de eroare ale interfeței publice este parte a *test specification* care trebuie verificată.
3. În practică industrială (cf. Khorikov [2], cap. 3 — *"What makes a good unit test"*), aserțiile pe mesajele de eroare sunt comune când mesajul transportă informație critică pentru consumator (logging, monitoring, alerting, UI).

Conform acestor referințe, mutantul **alterează contractul observabil al funcției** și NU este echivalent în sensul "strong mutation". Pentru completitudine, scriem un test care îl distinge (vezi §24.2).

### 23.2 Mutant #6 (linia 11, mesaj `EmptyCargoListError`)

```diff
-            raise EmptyCargoListError("Lista de marfuri nu poate fi goala")
+            raise EmptyCargoListError("XXLista de marfuri nu poate fi goalaXX")
```

![Diff mutant #6](<screenshots/mutmut_show_6.png>)

**De ce a supraviețuit?** Identic cu #3 — textul mesajului nu este verificat în testele BB+WB.

**Clasificare: NON-ECHIVALENT la nivel de contract observabil** (același raționament și aceleași referințe ca §23.1). Test de distingere: §24.3.

### 23.3 Mutant #18 (linia 25, frontiera `hazardous_weight`)

```diff
-        if hazardous_weight > 0 and ratio > 0.7:
+        if hazardous_weight > 1 and ratio > 0.7:
```

![Diff mutant #18](<screenshots/mutmut_show_18.png>)

**De ce a supraviețuit?** Testele BB+WB folosesc cargo periculos cu greutate de 30t sau 80t. În ambele cazuri `hazardous_weight > 1` este adevărat, deci mutantul produce același rezultat ca originalul. Cazul `hazardous_weight = 1` exact (singura valoare unde `> 0` este True dar `> 1` este False) NU este testat.

**Clasificare: NON-ECHIVALENT (logic, strict semantic).** Este un mutant clasic de operator relațional / valoare de frontieră — exact tipul de defect pe care BVA și mutation testing sunt menite să-l prindă. Diferența comportamentală e demonstrabilă: pentru orice input cu `hazardous_weight = 1` și `ratio > 0.7`, original returnează `"HIGH"` iar mutantul returnează altceva. Test de distingere: §24.1.

### 23.4 Tabel rezumativ

| Mutant | Linie | Diff | Tip mutație | Clasificare |
|---|---|---|---|---|
| #3 | 9 | mesaj `NegativeDelayError` cu prefix/sufix `XX` | string literal | non-echivalent (contract observabil, strong mutation) |
| #6 | 11 | mesaj `EmptyCargoListError` cu prefix/sufix `XX` | string literal | non-echivalent (contract observabil, strong mutation) |
| #18 | 25 | `> 0` → `> 1` în condiția compusă D4 | constant numeric / frontieră | non-echivalent (logic, semantic) |

**Toți 3 mutanți supraviețuitori sunt clasificați NON-ECHIVALENȚI.** Cerința T1 cere ≥ 2 teste suplimentare care să omoare ≥ 2 mutanți non-echivalenți → vom omorî pe toți 3 (depășire).

---

## 24. Teste suplimentare pentru omorârea mutanților

Cele 3 teste sunt în `tests/test_risk_evaluator_mutation.py`. Cerința minimă a profesoarei (2 teste, 2 mutanți) este **depășită** — am scris 3 teste care omoară toți 3 supraviețuitorii.

### 24.1 Test pentru mutant #18

```python
def test_kill_mut_18_hazardous_weight_threshold_at_1t(train_100t_80kmh, route_450_diff1):
    cargo_list = [
        Cargo("Marfa normala", 75.0),
        Cargo("Marfa periculoasa", 1.0, is_hazardous=True),
    ]
    result = RiskEvaluator().evaluate_shipment_risk(cargo_list, train_100t_80kmh, route_450_diff1, 0)
    assert result == "HIGH"
```

**Analiza condițiilor de omorâre:**

| Condiție | Argumentare |
|---|---|
| Reachability | `hazardous_weight = 1` (exact 1t marfă periculoasă), `ratio = 0.76 > 0.7` ⇒ instrucțiunea mutată D4 este ATINSĂ |
| State infection | Original: `1 > 0 ∧ 0.76 > 0.7 = T` ⇒ ramura `return "HIGH"`. Mutant: `1 > 1 ∧ 0.76 > 0.7 = F` ⇒ continuă pe alt drum (D5=F → D6=T → MEDIUM) ⇒ STAREA diferă |
| State propagation | Diferența de stare se propagă la ieșire: `"HIGH"` (original) vs `"MEDIUM"` (mutant). Asertia `assert result == "HIGH"` PRINDE diferența ⇒ test FAIL pe mutant |

### 24.2 Test pentru mutant #3

```python
def test_kill_mut_3_neg_delay_error_message_prefix(...):
    with pytest.raises(NegativeDelayError) as exc_info:
        RiskEvaluator().evaluate_shipment_risk([cargo_normal], train_100t_80kmh, route_450_diff1, -1)
    msg = str(exc_info.value)
    assert msg.startswith("Intarzierea nu poate fi negativa")
    assert "-1" in msg
```

**Analiza:** `delay = -1` ⇒ ramura D1=T este atinsă (reachability), instrucțiunea mutată construiește un mesaj cu prefix `"XX"` (state infection), care se propagă la mesajul excepției (state propagation). Asertia `.startswith("Intarzierea")` eșuează pe mutant (mesajul mutat începe cu `"XX"`).

### 24.3 Test pentru mutant #6

```python
def test_kill_mut_6_empty_cargo_error_message_exact(train_100t_80kmh, route_450_diff1):
    with pytest.raises(EmptyCargoListError) as exc_info:
        RiskEvaluator().evaluate_shipment_risk([], train_100t_80kmh, route_450_diff1, 0)
    msg = str(exc_info.value)
    assert msg == "Lista de marfuri nu poate fi goala"
```

**Analiza:** `cargo_list = []` ⇒ D2=T atinsă, mesajul mutat are caractere `"XX"` în plus, asertia `==` (egalitate strictă) eșuează pe mutant.

### 24.4 Re-rulare mutmut după teste suplimentare (rulare FINALĂ)

După adăugarea fișierului `test_risk_evaluator_mutation.py` în runner (vezi §21.3.B):

| Categorie | Înainte (BB+WB) | După (BB+WB+mutation) |
|---|---|---|
| Omorâți | 32 | **35** |
| Supraviețuitori | 3 | **0** |
| Total | 35 | 35 |

**Captură de ecran cu output-ul `mutmut run` — rulare finală:**

![Output mutmut rulare finală - 35 omorâți, 0 supraviețuitori](<screenshots/mutmut_final_run.png>)

**Captură de ecran cu cache-ul SQLite — rulare finală:**

![Cache mutmut SQLite - 35 ok_killed, 0 bad_survived](<screenshots/mutmut_final_sqlite.png>)

### 24.5 Mutation score final

```
MS_final = D / (D + L_neechiv) = 35 / (35 + 0) = 35/35 = 100%
```

---

## 25. Interpretarea finală (toate cele 3 etape)

**1. Eficiența combinată a strategiilor.**
- Black-box (EC + BVA): **23 teste** → coverage 100%, dar 3 mutanți supraviețuitori (testele BB nu verifică textul excepțiilor și nu testează frontiera `hazardous_weight = 1`).
- White-box (statement, branch, condition, paths): **+36 teste** → ilustrare structurală explicită; nu îmbunătățește coverage (deja 100%) dar nu rezolvă nici toți supraviețuitorii mutmut (focusul WB este pe căi, nu pe valori specifice).
- Mutation testing: **+3 teste** → omoară toți 3 supraviețuitorii rămași, confirmând că suita combinată e robustă.

**2. Validare a principiului "100% coverage ≠ teste perfecte".** Suita BB + WB avea coverage 100% statement și 100% branch, dar mutmut a identificat 3 mutanți pe care îi rata. Asta confirmă observația din [Curs Coverage Testing §10] și exemplul `isPrime`: coverage-ul nu detectează:
- Lipsa verificării conținutului mesajelor (mutanții #3, #6).
- Defecte la frontiere absolute (mutantul #18 cere testarea exactă a `haz_weight = 1`).

**3. Coupling effect ipotetic confirmat empiric.** Cele 3 teste pe mutanți de ordinul 1 ar prinde și mutanți de ordinul mai mare construiți peste aceleași locații. De exemplu, un mutant care schimbă **ambele** `> 0` → `> 1` AND `> 0.7` → `> 0.71` ar fi prins de testul `test_kill_mut_18_hazardous_weight_threshold_at_1t`.

**4. Limitele rămase.** Mutmut nu testează:
- Erori de design / arhitectură (alegerea greșită a algoritmului).
- Erori de specificație (regulile însele pot fi greșite).
- Concurență, race conditions (nu aplicabil pentru SUT-ul nostru, e funcție pură).
- Probleme de performanță sau memorie.

**5. Concluzie agregată.** Cu **164 de teste totale**, **100% coverage** și **100% mutation score** pe SUT-ul principal, suita atinge limitele superioare practice ale celor 3 strategii combinate. Cerințele T1 sunt îndeplinite integral:

| Cerință T1 | Status |
|---|---|
| Partiționare în clase de echivalență | ✅ §4.1, §5.x |
| Analiza valorilor de frontieră | ✅ §4.2, §8.4 |
| Acoperire la nivel de instrucțiune | ✅ §14 (100%) |
| Acoperire la nivel de decizie | ✅ §15 (100%) |
| Acoperire la nivel de condiție | ✅ §16 (100%) |
| Circuite independente | ✅ §17 (V(G)=8, set de bază) |
| Analiză raport mutanți | ✅ §22, §23 |
| ≥ 2 teste suplimentare pentru ≥ 2 mutanți non-echiv | ✅ §24 (3 teste, 3 mutanți) |
| SUT cu ≥ 3 params, loop, 2 conditionale (cu/fara else), simplă + compusă | ✅ §5.5 |

---

## Anexă A. Cum se reproduc rezultatele

```bash
# 1. Activare mediu virtual
source .venv/Scripts/activate              # Git Bash
# .venv\Scripts\Activate.ps1               # PowerShell

# 2. Instalare dependinte
pip install pytest coverage
pip install "mutmut==2.4.5" "pony<0.7.18"  # versiuni specifice (vezi §21.1)

# 3. Rulare suita completa
.venv/Scripts/python -m pytest tests/ -v

# 4. Rulare doar pe SUT-ul principal (BB + WB + mutation)
.venv/Scripts/python -m pytest \
    tests/test_risk_evaluator_blackbox.py \
    tests/test_risk_evaluator_whitebox.py \
    tests/test_risk_evaluator_mutation.py -v

# 5. Lista teste fara rulare (audit EC/BVA/circuite)
.venv/Scripts/python -m pytest tests/ --collect-only -q

# 6. Coverage statement + branch pe SUT (raport HTML)
.venv/Scripts/python -m coverage erase
.venv/Scripts/python -m coverage run --branch --source=service.risk_evaluator -m pytest \
    tests/test_risk_evaluator_blackbox.py \
    tests/test_risk_evaluator_whitebox.py \
    tests/test_risk_evaluator_mutation.py
.venv/Scripts/python -m coverage report -m
.venv/Scripts/python -m coverage html -i
# Deschide htmlcov/index.html in browser

# 7. Mutation testing pe SUT
PYTHONIOENCODING=utf-8 .venv/Scripts/python -m mutmut run \
    --paths-to-mutate=service/risk_evaluator.py \
    --runner=".venv\Scripts\python.exe -m pytest tests/test_risk_evaluator_blackbox.py tests/test_risk_evaluator_whitebox.py tests/test_risk_evaluator_mutation.py -x -q --no-header"

# 8. Vizualizare diff mutanti supravietuitori (daca exista)
.venv/Scripts/python -m mutmut show <id>

# 9. Citire cache mutanti (SQLite, workaround Python 3.13)
.venv/Scripts/python -c "
import sqlite3
con = sqlite3.connect('.mutmut-cache')
for row in con.execute('SELECT status, COUNT(*) FROM Mutant GROUP BY status'):
    print(row)
"
```
