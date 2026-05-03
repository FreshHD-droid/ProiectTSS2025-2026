# Transport Feroviar de Marfă — Proiect TSS T1

> **Disciplină:** Testarea Sistemelor Software (TSS), FMI, anul III, sem. II
> **Tema:** T1 — Testare unitară în Python
> **An universitar:** 2025-2026
> **Echipa:** Marcu George Robert, Brișiț Mario Vlad

Aplicație CLI în Python care modelează planificarea transportului feroviar de marfă (trenuri, rute, mărfuri, planuri). Proiectul demonstrează strategiile de testare unitară din curs aplicate end-to-end pe SUT-ul principal: clasa `RiskEvaluator` cu metoda `evaluate_shipment_risk`.

## 📊 Metrici cheie

| Metrică | Valoare |
|---|---|
| Teste totale | **164** (125 BB + 36 WB + 3 mutation) — toate trec |
| Statement coverage | **100%** (22/22 statements) |
| Branch coverage | **100%** (14/14 branches) |
| Mutation score | **100%** (35/35 mutanți omorâți) |
| Cyclomatic complexity V(G) | 8 |

## 📁 Documentația principală

- 📄 **[documentatie_proiect.md](documentatie_proiect.md)** — documentația completă (BB + WB + mutation, ~1010 linii)

## 🚀 Comenzi rapide

```bash
# Activare mediu virtual
source .venv/Scripts/activate              # Git Bash
# sau: .venv\Scripts\Activate.ps1         # PowerShell

# Instalare dependinte
pip install pytest coverage
pip install "mutmut==2.4.5" "pony<0.7.18"

# Rulare suita completa
.venv/Scripts/python -m pytest tests/ -v   # 164 passed

# Coverage statement + branch pe SUT
.venv/Scripts/python -m coverage erase
.venv/Scripts/python -m coverage run --branch --source=service.risk_evaluator -m pytest \
    tests/test_risk_evaluator_blackbox.py \
    tests/test_risk_evaluator_whitebox.py \
    tests/test_risk_evaluator_mutation.py
.venv/Scripts/python -m coverage report -m
.venv/Scripts/python -m coverage html -i  # raport HTML in htmlcov/

# Mutation testing (vezi documentatie_proiect.md §21.3 pentru detalii)
PYTHONIOENCODING=utf-8 .venv/Scripts/python -m mutmut run \
    --paths-to-mutate=service/risk_evaluator.py \
    --runner=".venv\\Scripts\\python.exe -m pytest tests/test_risk_evaluator_blackbox.py tests/test_risk_evaluator_whitebox.py tests/test_risk_evaluator_mutation.py -x -q --no-header"
```

## 🗂 Structura proiectului

```
Proiect_TSS_v2/
├── domain/              # Cargo, FreightTrain, Route, TransportPlan
├── service/             # TransportService, RiskEvaluator (SUT principal)
├── exceptions/          # 9 excepții custom (subclase ValueError)
├── ui/                  # CLI (main.py)
├── tests/               # 164 teste (BB + WB + mutation)
│   ├── conftest.py
│   ├── test_cargo_blackbox.py
│   ├── test_freight_train_blackbox.py
│   ├── test_route_blackbox.py
│   ├── test_transport_plan_blackbox.py
│   ├── test_risk_evaluator_blackbox.py     # 23 teste BB
│   ├── test_risk_evaluator_whitebox.py     # 36 teste WB
│   └── test_risk_evaluator_mutation.py     # 3 teste mutation kill
├── Diagrame/            # PNG-uri export draw.io + sursa CFG
├── screenshots/         # Capturi rulare teste, coverage, mutmut
├── archive/             # Documente vechi (etapa 1/3)
├── Project_Context/     # Materiale curs (referință)
├── Project_Tasks/       # Specificația temei
├── documentatie_proiect.md
├── prezentare.md
├── raport_ai.md
└── main.py              # Entry point CLI
```

## 📋 Strategii aplicate (T1)

| Strategie | Locație în `documentatie_proiect.md` |
|---|---|
| Partiționare clase de echivalență (EC) | §4.1, §5.x |
| Analiza valorilor de frontieră (BVA) | §4.2, §8.4 |
| Statement coverage | §14 |
| Decision/Branch coverage | §15 |
| Condition coverage | §16 |
| Circuite independente (McCabe) | §17 |
| Analiză raport mutanți | §22, §23 |
| Teste suplimentare → mutanți non-echivalenți | §24 |
