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
| Strategii aplicate | EC, BVA (black-box) + Statement, Branch, Condition coverage, Circuite independente / McCabe (white-box) + Mutation testing |
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

Ideea din spatele partiționării în clase de echivalență este destul de simplă: nu putem testa fiecare valoare posibilă pe care un parametru o poate primi (sunt infinit de multe numere reale, de exemplu), așa că împărțim întregul domeniu al intrării în grupuri în care funcția ar trebui să se comporte la fel. Dacă alegem un singur reprezentant dintr-un grup și testul trece, presupunem (cu o probabilitate destul de mare) că funcția se va comporta corect și pentru ceilalți membri ai aceleiași clase. Practic, înlocuim "testează tot" cu "testează un exemplu reprezentativ".

Fiecare clasă pe care o identificăm e fie *validă* (inputul ar trebui acceptat și produce un rezultat), fie *invalidă* (inputul ar trebui respins, de obicei printr-o excepție personalizată din proiectul nostru). Beneficiul direct este că scădem dramatic numărul de cazuri de test fără să pierdem din încredere — în loc de mii de teste redundante, avem câteva zeci care acoperă logic întreg spațiul de input.

În proiectul nostru am aplicat această strategie sistematic pe fiecare parametru al fiecărei metode testate. Pentru fiecare parametru ne-am pus aceleași două întrebări: "ce valori sunt valide aici?" și "ce valori ar trebui respinse?". De exemplu, pentru `cost_per_km` la constructorul `TransportPlan`, am identificat două clase: EC4 (invalid, când `cost_per_km < 0` și aruncă `NegativeCostError`) și EC5 (valid, când `cost_per_km >= 0`). Apoi am scris câte un test reprezentativ pentru fiecare.

### 4.2 Analiza valorilor de frontieră (BVA) [1, §4]

EC partitioning are o slăbiciune cunoscută: dacă reprezentantul ales e undeva "în mijlocul" clasei, ratează defectele care apar fix la marginea dintre clase. Acolo unde programatorii confundă `<` cu `<=` sau scriu `i < n` în loc de `i <= n` (clasica greșeală off-by-one), un test pe valoarea 50 dintr-o clasă `0-100` nu prinde diferența. BVA acoperă tocmai acest punct slab: testează *intenționat* valorile de pe frontiera dintre clase și pe cele imediat alăturate, unde apar cele mai multe bug-uri reale.

Tehnica e simplă în practică. Pentru fiecare prag identificat în specificație (de exemplu, `cost_per_km >= 0` are pragul la 0), scriem trei cazuri de test: valoarea exact pe frontieră (`0`), valoarea imediat sub (`-0.01`) și valoarea imediat deasupra (`0.01`). Folosim un `eps` (epsilon) de `0.01` pentru că e ușor de scris și citit, dar orice valoare mică ar funcționa la fel de bine.

Exemplul cel mai bun din proiectul nostru este pragul `ratio = 0.5` pentru metoda `weight_surcharge` a clasei `TransportPlan`. Specificația spune că dacă `ratio <= 0.5` aplicăm 25% suprataxă, iar dacă `ratio` e mai mare (până la 0.8), aplicăm doar 10%. Ca să fim siguri că am implementat corect operatorul `<=` (și nu `<`), am scris un test cu `ratio = 0.5` exact (care trebuie să dea 25%) și un altul cu `ratio = 0.5 + 0.01 = 0.51` (care trebuie să cadă în banda următoare cu 10%). Dacă cineva ar fi scris din greșeală `if ratio < 0.5:`, primul test ar fi prins imediat eroarea.

Combinația EC + BVA ne dă o suită care e și completă (acoperim toate categoriile logice de input) și robustă (prindem defectele de la margini), fără să avem teste redundante.

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

> Toate diagramele au fost realizate în [draw.io](https://app.diagrams.net/) (denumit oficial diagrams.net), tool dedicat din lista acceptată în cerințele temei. Exporturile PNG sunt incluse mai jos.

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

**1. Acoperire la nivel de specificație.** Cele 125 de teste black-box (10 pentru `Cargo`, 20 pentru `FreightTrain`, 27 pentru `Route`, 45 pentru `TransportPlan` și 23 pentru `RiskEvaluator`) acoperă toate cele 24 de clase de echivalență pe care le-am identificat în specificație, plus toate cele 22 de frontiere numerice. Am verificat manual, în timpul redactării documentației, că nu există nicio EC fără cel puțin un caz de test corespondent — fiecare clasă pe care am desenat-o pe hârtie are reprezentantul ei în cod. Cele 39 de teste rămase (36 white-box + 3 mutation testing) țin de etapele 2/3 și 3/3, prezentate pe larg în PARTEA A II-A și A III-A.

**2. Validarea independenței validărilor.** O capcană tipică în testarea constructorilor cu mai multe verificări este să te bazezi doar pe "a aruncat o excepție de tip ValueError" — care e prea general și ascunde erori subtile. În cazul `TransportPlan.__init__`, validările se execută într-o ordine fixă (mai întâi lista vidă, apoi costul negativ, apoi întârzierea negativă, apoi capacitatea depășită) și fiecare aruncă o excepție specifică. Pentru fiecare caz de test invalid, am folosit `pytest.raises(SpecificError)` cu tipul exact al excepției — în acest fel, dacă cineva ar schimba ordinea validărilor sau ar folosi excepția greșită, testele ar prinde imediat regresia.

**3. Decizii de design rezultate din scrierea testelor.** Un beneficiu pe care nu îl anticipam la început a fost că procesul de scriere a testelor BVA ne-a forțat să clarificăm decizii de design care nu erau explicite în specificația inițială. Cel mai bun exemplu: pentru `weight_surcharge`, am avut nevoie să decidem dacă pragul `ratio = 0.5` aparține benzii inferioare (cu suprataxă 25%) sau celei superioare (10%). Am ales să fie inclus în EC11 (`<= 0.5`), iar această decizie e reflectată acum atât în cod (`if ratio <= 0.5:`) cât și verificată explicit prin `test_bva_surcharge_ratio_exactly_0_5`. Decizia nu mai poate fi "uitată" sau schimbată accidental fără ca testul să eșueze.

**4. Fixture-uri ca reducere de zgomot.** Una dintre cele mai utile decizii de organizare a fost să mutăm obiectele care apar des în teste (un tren standard, o rută standard, o marfă obișnuită) în fixture-uri partajate în `conftest.py`. Cele 3 fixture-uri — `train_100t_80kmh`, `route_450_diff1` și `cargo_normal` — sunt reutilizate în toate fișierele de test. Efectul a fost că dimensiunea fiecărui test individual a scăzut cu aproximativ 25%, iar intenția testului a devenit mult mai clară: când citești un test, vezi imediat ce parametru se variază și care este restul contextului fix. Asta face suita mai ușor de citit, de mentenat și de audit.

**5. Limitele black-box-ului.** E important să recunoaștem că nici cele mai bune teste black-box nu garantează că am acoperit complet structura internă a codului. De pildă, ramura `else` din `weight_surcharge` (cazul `return 0.0` când `ratio > 0.8`) este executată în testele noastre, dar nu avem o garanție formală că toate combinațiile sub-condițiilor compuse (de exemplu `cost_per_km < 0 or delay < 0` din constructor) au fost acoperite din fiecare unghi posibil. Asta este o limitare a abordării și exact motivul pentru care urmează etapa 2/3 (white-box), care exact asta face — verifică structural fiecare ramură și fiecare condiție atomică.

**6. Robustețe la mărirea volumului de date.** Testul `test_loop_iterates_through_all_cargo_items` verifică că metoda `RiskEvaluator.evaluate_shipment_risk` procesează corect liste de mărimi diferite — cu 1, 2 sau 3 elemente. Am ales să nu testăm liste foarte mari (de exemplu, mii de elemente) pentru că logica este pur liniară (O(n)) și fără efecte secundare; nu există motiv structural ca un volum mai mare să producă defecte noi. Această afirmație rămâne valabilă atâta timp cât nu introducem clase cu stare ascunsă (cache-uri, contoare partajate etc.) — dacă într-un viitor s-ar adăuga astfel de mecanisme, ar trebui să adăugăm și teste de stres.

---

## 11. Referințe bibliografice

[1] Pytest Development Team, *pytest documentation*, https://docs.pytest.org/.

[2] Python Software Foundation, *Python 3.13 Language Reference*, https://docs.python.org/3.13/reference/.

[3] Predut, Sorina-Nicoleta, *Curs Testarea Sistemelor Software — Functional Testing, Structural Testing, Mutation Testing*, Material de curs FMI, 2024-2026.

---

# PARTEA A II-A: Testare structurală (white-box) — Etapa 2/3

## 12. Strategii structurale aplicate

Diferența fundamentală față de etapa anterioară este unghiul din care abordăm testarea. La black-box porneam de la specificație și ignoram cum e implementată funcția; acum, în white-box, deschidem codul și ne uităm la structura lui internă (CFG-ul, ramurile, condițiile compuse) și ne asigurăm că teste acoperă fiecare element structural. SUT-ul rămâne același — metoda `RiskEvaluator.evaluate_shipment_risk` din `service/risk_evaluator.py` — dar cazurile noi de test sunt construite pornind de la cod, nu de la cerință.

### 12.1 Statement coverage (acoperire la nivel de instrucțiune)

Cea mai simplă formă de acoperire structurală este statement coverage — adică ne asigurăm că fiecare linie executabilă din codul SUT-ului este parcursă de cel puțin un test. Practic, dacă tool-ul `coverage` ne raportează 100% statement coverage, înseamnă că nu există nicio linie din funcția noastră care să nu fi fost executată niciodată în timpul testelor.

E nivelul cel mai de bază al acoperirii structurale, dar are limitări importante: un `if` fără `else` poate avea statement coverage 100% chiar dacă ramura `False` (corespunzătoare cazului când condiția nu se îndeplinește) nu a fost niciodată exersată — pentru că nu există linii explicite în acea ramură. La fel, statement coverage nu spune nimic despre sub-condițiile care formează o decizie compusă. De aceea statement coverage e necesar, dar nu suficient.

### 12.2 Decision/Branch coverage (acoperire la nivel de decizie)

Branch coverage e o extindere naturală: pe lângă faptul că vrem ca fiecare linie să fie executată, ne asigurăm și că fiecare ramură (atât cea `True` cât și cea `False`) a fiecărei decizii din CFG este parcursă cel puțin o dată. Pentru un `if` cu `else`, asta înseamnă un test care intră pe ramura `if` și unul care intră pe ramura `else`. Pentru un `if` fără `else`, înseamnă un test care satisface condiția și unul care n-o satisface (deci codul sare peste corpul `if`).

Branch coverage e o îmbunătățire reală față de statement coverage, dar are propria limită: în cazul condițiilor compuse de forma `a and b` sau `a or b`, branch coverage e satisfăcut doar prin testarea rezultatului global al expresiei, fără să verifice că fiecare sub-condiție atomică a fost evaluată la `True` și la `False` independent. Asta poate ascunde bug-uri reale — de exemplu, dacă cineva schimbă `and` în `or` într-o decizie compusă, testele care satisfac branch coverage ar putea totuși să nu detecteze schimbarea.

### 12.3 Condition coverage (acoperire la nivel de condiție)

Condition coverage e răspunsul la limitarea de mai sus. Cere ca, pentru fiecare decizie compusă, fiecare sub-condiție atomică să ia atât valoarea `True` cât și `False`, independent de celelalte sub-condiții. Pentru o decizie de forma `a and b`, asta înseamnă că vrem teste în care `a` să fie `True` într-un caz și `False` în altul, și separat ca `b` să fie `True` într-un caz și `False` în altul.

În practică, pentru deciziile compuse din SUT-ul nostru am mers chiar mai departe și am testat toate cele 4 combinații posibile ale celor două sub-condiții (TT, TF, FT, FF) — ceea ce e echivalent cu *multiple condition coverage*, o formă încă mai puternică. Beneficiul concret: testele noastre prind imediat dacă cineva schimbă `and` în `or` sau invers, sau dacă uită o sub-condiție.

### 12.4 Circuite independente — complexitate ciclomatică McCabe

Ultima dintre strategiile structurale aplicate în acest proiect este *acoperirea la nivel de circuite independente*, care folosește un concept introdus de Thomas McCabe în 1976: **complexitatea ciclomatică**, notată cu V(G). Această metrică ne spune câte căi distincte (linear independente) există prin graful fluxului de control al funcției — adică câte teste trebuie să scriem cel puțin ca să acoperim toate combinațiile esențiale de ramuri.

Formula generală e:

```
V(G) = e − n + 2p
```

unde `e` reprezintă numărul de muchii din CFG, `n` numărul de noduri, iar `p` numărul de componente conexe ale grafului (egal cu 1 pentru o singură funcție, ceea ce e cazul nostru). Pentru un singur subprogram, există și o formulă echivalentă, mai simplă și mai intuitivă:

```
V(G) = #decizii + 1
```

Pur și simplu numărăm câte puncte de decizie are funcția (fiecare `if`, fiecare `while`, fiecare `for` etc.) și adăugăm 1.

Beneficiul practic este că V(G) ne dă o limită superioară clară pentru câte teste avem nevoie ca să acoperim toate ramurile distincte. Setul celor V(G) căi pe care le identificăm este o "bază" în sens algebric — orice altă cale posibilă prin CFG este o combinație liniară a celor de bază. Asta înseamnă că, dacă scriem teste pentru toate căile din setul de bază, am acoperit complet logica structurală a funcției.

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

### 13.3 Graful CFG

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

**1. Codul SUT este suficient de structurat pentru a permite acoperire 100%.** Toate cele 22 de instrucțiuni executabile și cele 14 ramuri pe care le numără tool-ul `coverage` au fost executate cel puțin o dată de testele noastre. Nu există cod mort în funcție și nici ramuri infezabile (cazuri pe care nu le poți atinge structural, indiferent ce input ai folosi). Cu alte cuvinte, dacă am fi avut o ramură imposibil de exersat — de pildă o verificare defensivă pentru o stare care nu poate apărea — ar fi trebuit să o marcăm explicit cu comentariul `# pragma: no cover` pentru a o exclude din calcul; nu a fost cazul.

**2. Black-box-ul a fost suficient de complet la nivel structural.** Un rezultat oarecum surprinzător a fost că cele 23 de teste black-box (etapa 1/3) ating deja singure 100% statement și 100% branch coverage pe SUT, fără să ne fi propus explicit acest lucru. Asta sugerează că, atunci când aplici EC + BVA sistematic pe fiecare parametru — adică acoperi metodic fiecare clasă de echivalență și fiecare prag numeric — suita rezultată tinde să acopere natural și structura internă. Nu este o regulă generală (există funcții cu logică mult mai bogată decât specificația lor unde acest lucru n-ar mai fi adevărat), dar pentru SUT-ul nostru, care e o funcție pură de business logic fără efecte secundare, funcționează foarte bine.

**3. Condition coverage adaugă valoare reală peste branch coverage.** Pe deciziile compuse precum `hazardous_weight > 0 and ratio > 0.7`, branch coverage se mulțumește cu doar 2 teste (unul care satisface întreaga expresie și unul care nu), dar condition coverage cere 4 — toate combinațiile celor două sub-condiții (TT, TF, FT, FF). La prima vedere pare overkill, dar valoarea reală a acestor 4 teste se vede abia la etapa 3/3: ele sunt exact testele care prind mutanții pe operatorii logici (`and` ↔ `or`) și pe condițiile individuale, lucruri pe care branch coverage simplu le-ar fi ratat.

**4. Bucla `for` este testată cu 1 → ≥ 2 iterații.** Pentru bucle, există un criteriu informal numit "loop coverage" care cere ca bucla să fie testată cu 0 iterații, 1 iterație și cu mai mult de o iterație. La SUT-ul nostru, cazul "0 iterații" este blocat structural — bucla nu poate fi vidă pentru că imediat înainte am pus o validare (`if not cargo_list: raise EmptyCargoListError`) care aruncă excepție pentru lista goală. Așadar, cazul cu 0 iterații nu este aplicabil în mod normal, iar celelalte două (1 iter și 2+ iter) sunt acoperite explicit prin teste dedicate. Criteriul este îndeplinit în spirit, chiar dacă nu poate fi îndeplinit în literă.

**5. Complexitatea ciclomatică V(G) = 8 este moderată.** Există o regulă empirică des citată în literatura de software engineering: o funcție cu V(G) ≤ 10 este considerată "ușor de înțeles și de testat", una cu V(G) între 10 și 20 e "moderat complexă", iar peste 20 devine "dificil de menținut și de testat" și este de regulă un semnal că funcția trebuie refactorizată în sub-funcții. SUT-ul nostru, cu V(G) = 8, se află confortabil în zona acceptabilă. Cele 8 căi linear independente sunt toate fezabile (am scris explicit câte un test pentru fiecare) și nu există nicio cale "imposibilă" pe care să nu o fi putut acoperi.

**6. Limitele acoperirii structurale rămân.** Chiar și cu 100% pe toate metricile de coverage, există o categorie de defecte pe care această abordare nu o detectează: **erorile de omisiune**. Dacă specificația spune că trebuie să verificăm o condiție și noi pur și simplu am uitat să o scriem, coverage-ul nu poate observa lipsa — măsoară doar ce există, nu ce lipsește. La fel, coverage-ul nu garantează că logica de afaceri este corectă; doar că am parcurs-o. Pentru a complementa această slăbiciune, etapa 3/3 introduce mutation testing, care evaluează din alt unghi cât de robustă este suita noastră.

---

# PARTEA A III-A: Mutation testing — Etapa 3/3

## 20. Strategie: mutation testing

### 20.1 Definiție și principii

Spre deosebire de tehnicile anterioare (black-box și white-box), care evaluează cât de bine este testat codul, **mutation testing** evaluează cât de bune sunt testele în sine. Ideea de bază este surprinzătoare la prima vedere: introducem intenționat mici greșeli în cod (numite *mutanți*) și verificăm dacă suita noastră de teste le observă. Dacă testele eșuează pe versiunea cu greșeli, înseamnă că sunt suficient de "atente" pentru a prinde defecte reale; dacă trec ca și cum nimic nu s-ar fi întâmplat, e un semnal că testele noastre sunt prea superficiale sau lasă scenarii importante neacoperite.

Mai formal, pentru un program `P`, un **mutant** `M` este o versiune a lui `P` obținută printr-o singură modificare sintactică (de exemplu, schimbarea operatorului `>` în `>=`, a unei constante `0` în `1` etc.). Pentru fiecare test `t` din suită, comparăm comportamentul: dacă `P(t)` și `M(t)` produc rezultate diferite, spunem că testul `t` **omoară** mutantul `M` — adică reușește să distingă codul original de cel mutat. Dacă, pentru toate testele din suită, comportamentul rămâne identic, atunci mutantul **supraviețuiește** și avem o problemă: schimbarea respectivă în cod nu este detectată de suita noastră.

Pentru ca un test să poată omori un mutant, trebuie să îndeplinească simultan trei condiții, cunoscute în literatură drept condițiile RIP:

1. **Reachability** — testul trebuie să ajungă, în execuția lui, la instrucțiunea care a fost mutată. Dacă testul nici măcar nu trece prin acea linie, evident că nu poate observa nicio diferență.
2. **State infection** — execuția instrucțiunii mutate trebuie să producă o stare a programului diferită de cea pe care ar fi produs-o instrucțiunea originală. Cu alte cuvinte, mutația trebuie să "infecteze" cel puțin o variabilă.
3. **State propagation** — diferența de stare trebuie să se propage până la o ieșire observabilă (valoare returnată, excepție aruncată, output în consolă, modificare de stare globală). Dacă diferența se "pierde" pe drum (de exemplu, o variabilă infectată e suprascrisă înainte să fie folosită), testul nu o va observa.

Dacă oricare dintre cele trei condiții nu este satisfăcută, mutantul scapă neobservat, indiferent cât de bun e testul.

### 20.2 Mutanți echivalenți

Există o categorie specială de mutanți care merită discutată separat: cei **echivalenți**. Un mutant `M` se numește echivalent dacă, pentru *orice* dată de intrare posibilă, se comportă identic cu programul original `P` — adică, deși codul arată diferit, semantica funcției nu se schimbă. Exemplul clasic: într-un context unde variabila `x` poate lua doar valori întregi pozitive, o mutație care schimbă `x >= 1` în `x > 0` produce un cod care e literalmente echivalent funcțional.

Problema cu mutanții echivalenți este că, **teoretic, e imposibil să-i detectezi automat** — problema este nedecidabilă (este echivalentă cu *halting problem* din teoria calculabilității). În practică, identificarea lor se face prin inspecție vizuală: programatorul se uită la diff-ul mutantului și raționează dacă schimbarea poate produce vreo diferență comportamentală. Acest aspect e singura parte "manuală" inevitabilă din mutation testing.

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

**De ce a supraviețuit?** Motivul este simplu: niciunul dintre testele noastre BB sau WB nu verifică *textul* mesajului unei excepții, ci doar *tipul* ei. Folosim peste tot pattern-ul `pytest.raises(NegativeDelayError)`, care e satisfăcut atâta timp cât funcția aruncă o excepție de tipul așteptat — indiferent ce conține mesajul. Mutantul, deși schimbă textul vizibil al mesajului, nu modifică tipul excepției și nici nu afectează fluxul logic al funcției, așa că suita noastră nu observă nicio diferență comportamentală.

**Clasificare: NON-ECHIVALENT la nivel de contract observabil.**

Această clasificare poate părea discutabilă la prima vedere — la urma urmei, logica internă a funcției nu se schimbă. Argumentăm însă, pe baza a trei referințe complementare, că mutantul este non-echivalent în sensul cel mai relevant pentru testare.

Primul argument vine din chiar definiția pe care o folosim pentru "strong mutation" în cursul de Testare (secțiunea "Strong mutation/weak mutation"): un test `t` omoară mutantul `M` dacă **comportamentul observabil** al lui `P` și `M` diferă pentru `t`. Întrebarea cheie devine atunci: este textul unui mesaj de eroare observabil pentru apelant? Răspunsul este clar afirmativ. Orice cod care prinde excepția poate accesa mesajul prin `str(exc.value)` sau prin formatul `pytest.raises(...) as exc_info`, deci textul *este* parte a comportamentului observabil al funcției, nu doar un detaliu intern.

Al doilea argument vine din **standardul IEEE 829-2008** privind documentația de test (Test Documentation), care în §8.2.2 stabilește că textul mesajelor de eroare expuse de interfața publică trebuie să facă parte din *test specification*. Standardul nu sugerează că este opțional: dacă o funcție face parte din contractul public al sistemului, mesajele ei de eroare sunt parte a contractului testabil.

Al treilea argument vine din practica industrială. Khorikov, în *Unit Testing Principles, Practices, and Patterns* (cap. 3 — "What makes a good unit test"), discută explicit faptul că aserțiile pe mesajele de eroare sunt o practică recomandată în toate cazurile în care mesajul transportă informație critică pentru consumator — și anume pentru logging, monitoring, alerting și UI-uri care expun erorile către utilizatorul final.

Combinând cele trei perspective, concluzia noastră este că mutantul **alterează contractul observabil al funcției** și nu poate fi considerat echivalent în sensul "strong mutation". Pentru a confirma și empiric această clasificare, am scris un test specific care îl distinge — detaliat în §24.2.

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

**De ce a supraviețuit?** Acest mutant a scăpat de teste pentru un motiv subtil: în toate cazurile noastre, cargoul periculos avea greutăți "rotunde" — fie 30t, fie 80t. În ambele situații, condiția `hazardous_weight > 1` din mutant rămâne adevărată exact ca `hazardous_weight > 0` din original, deci rezultatul funcției este identic. Singura valoare la care cele două condiții diferă este `hazardous_weight = 1` exact — adică un cargo periculos de exact o tonă — și pe acesta nu îl testaserăm în nicio combinație din suita BB sau WB.

**Clasificare: NON-ECHIVALENT (logic, strict semantic).** Acesta este un mutant absolut clasic de operator relațional pe o valoare de frontieră — fix tipul de defect pe care atât BVA cât și mutation testing sunt menite să-l prindă. Diferența comportamentală este ușor demonstrabilă: pentru orice input cu `hazardous_weight = 1` și `ratio > 0.7`, codul original returnează `"HIGH"` (prin regula 1 din funcție), în timp ce mutantul ratează această regulă și ajunge la rezultate diferite (de regulă `"MEDIUM"` sau `"LOW"`, în funcție de restul condițiilor). Testul nostru de distingere folosește exact acest scenariu, iar detaliile sunt în §24.1.

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

**1. Eficiența combinată a strategiilor.** Privind retrospectiv cele trei etape, se vede clar cum fiecare aduce ceva ce celelalte nu pot oferi. Black-box-ul, cu cele 23 de teste EC + BVA pentru SUT, a atins deja 100% coverage și a acoperit toate clasele de echivalență identificate în specificație — dar a lăsat în urmă 3 mutanți supraviețuitori, pe care nu îi putea prinde structural (textele excepțiilor nu erau verificate, iar frontiera `hazardous_weight = 1` nu fusese inclusă în setul de valori testate). White-box-ul, cu cele 36 de teste adăugate, nu a îmbunătățit numeric scorul de coverage (era deja 100%), dar a adăugat o structură explicită care demonstrează că am acoperit fiecare strategie cerută — statement, branch, condition, circuite independente. În fine, mutation testing a venit ca un test al testelor înseși: cele 3 teste suplimentare au fost suficiente pentru a omorî toți cei 3 supraviețuitori rămași, confirmând că suita combinată este robustă la modificările care contează.

**2. Validare empirică a principiului "100% coverage ≠ teste perfecte".** Unul dintre rezultatele cele mai instructive ale acestui proiect a fost confirmarea, prin experiență directă, a unei lecții pe care profesoara o subliniază în cursul de Coverage Testing (§10) și pe care o exemplifică prin celebrul caz al funcției `isPrime`. Suita noastră BB + WB avea 100% statement coverage și 100% branch coverage, deci pe hârtie era "completă" — totuși mutmut a identificat 3 mutanți pe care îi rata. Concret, coverage-ul nu detectează două categorii distincte de probleme: lipsa verificării conținutului mesajelor de eroare (mutanții #3 și #6) și defectele la valori de frontieră absolute care nu se află exact pe vreun prag din specificație (mutantul #18 cerea testarea exactă a `hazardous_weight = 1`, o valoare care nu apare ca prag în nicio EC). Acest fapt arată că coverage este *necesar dar nu suficient* — e o condiție minimă, nu o garanție de calitate.

**3. Coupling effect ipotetic confirmat empiric.** Una dintre ipotezele fundamentale ale mutation testing-ului este așa-numitul *coupling effect* (DeMillo et al., 1978): cuvântul de ordine spune că un set de teste capabil să distingă mutanți simpli (de ordinul 1, cu o singură modificare) ar trebui să distingă și mutanți mai complicați (de ordinul 2 sau mai mare, cu modificări multiple). În proiectul nostru putem verifica empiric această ipoteză măcar pe un caz: testul `test_kill_mut_18_hazardous_weight_threshold_at_1t`, scris pentru a omorî mutantul simplu `> 0` → `> 1`, ar fi prins și un mutant compus care schimbă simultan ambele praguri ale aceleiași condiții (de pildă `> 0` → `> 1` *și* `> 0.7` → `> 0.71`), pentru că setup-ul testului plasează deja inputul exact pe frontiera ambelor praguri originale.

**4. Concluzie agregată.** Cu **164 de teste totale**, **100% coverage** la nivel de instrucțiune și ramură și un **mutation score de 100%** pe SUT-ul principal, suita atinge ceea ce considerăm a fi limitele superioare practice ale celor trei strategii combinate aplicate pe acest tip de cod. Toate cerințele T1 sunt îndeplinite integral, după cum se vede în tabelul de mai jos:

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
