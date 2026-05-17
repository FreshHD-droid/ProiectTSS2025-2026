# Transport Feroviar de Marfă — Proiect TSS T1

> **Disciplină:** Testarea Sistemelor Software (TSS), FMI, anul III, sem. II
> **Tema:** T1 — Testare unitară în Python
> **An universitar:** 2025-2026
> **Echipa:** Marcu George Robert, Brișiț Mario Vlad

Aplicație CLI în Python care modelează planificarea transportului feroviar de marfă (trenuri, rute, mărfuri, planuri). Proiectul demonstrează **toate** strategiile de testare unitară din curs — *black-box*, *white-box* și *mutation testing* — aplicate end-to-end pe SUT-ul principal: clasa `RiskEvaluator` cu metoda `evaluate_shipment_risk`.

---

## 🔗 Linkuri rapide

| Resursa | Link | Format |
|---|---|---|
| 📄 Documentația completă | **[documentatie_proiect.md](documentatie_proiect.md)** | Markdown (~1010 linii) |
| 🎤 Prezentare | **[prezentare.md](prezentare.md)** | Remark.js + Markdown |
| 🎬 Demo video | https://youtu.be/hMOn0opYB18 | Video |
| 🤖 Raport AI tool | **[reportAI.md](reportAI.md)** | Markdown |
---

## 📊 Metrici cheie

| Metrică | Valoare |
|---|---|
| Teste totale | **164** (125 BB + 36 WB + 3 mutation) — toate trec |
| Statement coverage | **100%** (22/22 statements) |
| Branch coverage | **100%** (14/14 branches) |
| Mutation score | **100%** (35/35 mutanți omorâți) |
| Cyclomatic complexity V(G) | **8** |
| Clase de echivalență | **24** |
| Frontiere BVA | **22** |
| Timp rulare suită completă | **~0.15 s** |

---

## 🎯 Despre aplicație

**Transport Feroviar de Marfă** modelează un sistem de planificare a transportului feroviar. Funcționalități:

- **Definire entități**: trenuri (capacitate, viteză), rute (distanță, dificultate), mărfuri (greutate, periculos/fragil)
- **Plan de transport**: combinație tren + rută + listă mărfuri
- **Calcul automat**: cost de bază, suprataxă de greutate (3 benzi), penalizare de întârziere (4 benzi), durată estimată (ajustată cu factor cargo)
- **Comparare planuri**: alegere automată pe baza costului și duratei
- **Evaluare risc** (SUT principal): `RiskEvaluator.evaluate_shipment_risk` returnează `"LOW"`, `"MEDIUM"` sau `"HIGH"`
- **CLI interactiv**: meniu pentru CRUD + comparare + cascade-delete

---

## 🧪 Cele 3 etape de testare

| Etapa | Strategii | Teste adăugate | Cumulat |
|---|---|---|---|
| **1/3** (Black-box) | EC partitioning + BVA pe 4 clase domain + SUT | 125 | 125 |
| **2/3** (White-box) | Statement + Branch + Condition coverage + Circuite independente (McCabe) pe SUT | 36 | 161 |
| **3/3** (Mutation) | mutmut + 3 teste suplimentare → kill mutanți non-echivalenți | 3 | **164** |

Pentru detalii vezi `documentatie_proiect.md`:
- BB — §4 (teorie), §5 (subiecții), §8 (rezultate), §10 (interpretare)
- WB — §12-§19 (PARTEA A II-A)
- Mutation — §20-§25 (PARTEA A III-A)

---

## 🎤 Prezentare (≤10 slide-uri)

Fișierul **[prezentare.md](prezentare.md)** este un deck Remark.js + Markdown cu 10 slide-uri ce rezumă proiectul.

**Cum se vizualizează:**

1. Online (cel mai simplu): copiază conținutul fișierului pe https://remarkjs.com/remarkise → preview live.
2. Local: salvează un mic HTML wrapper (template Remark.js) lângă `prezentare.md` și deschide în browser.

Conține: deschiderea, SUT-ul + criterii T1, cele 3 etape (BB / WB / mutation), tabel kill mutanți, lecții învățate.

---

## 🎬 Demo video

> 🎥 **Link YouTube :** *https://youtu.be/hMOn0opYB18*

1. **CLI walkthrough** — creare tren / rută / cargo / plan, cascade-delete.
2. **Rulare teste + tool-uri** — `pytest -v` (164 passed), `coverage report` (100% / 100%), `mutmut run` (35/35 omorâți), vizualizare `htmlcov/index.html` în browser.

---

## 🤖 Raport AI tool

Fișierul **[reportAI.md](reportAI.md)** documentează folosirea **Gemini 3.1 Pro** (interfața web) pentru generarea automată a suitelor de teste black-box și white-box și **comparația** cu suita scrisă manual de noi (164 teste, 100% coverage, 100% mutation score). Codul generat de AI este disponibil în [`codAI/`](codAI/).

Structura raportului:
- §1 Tool ales + versiune
- §2 Metodologie (prompt folosit, procedură)
- §3 Diferențe specifice (teste lipsă AI vs unice ale echipei)
- §4 Interpretare (avantaje, limite, concluzie)

---

## 🚀 Comenzi rapide

### Setup

```bash
# Activare mediu virtual
source .venv/Scripts/activate              # Git Bash
# sau: .venv\Scripts\Activate.ps1         # PowerShell

# Instalare dependinte
pip install pytest coverage
pip install "mutmut==2.4.5" "pony<0.7.18"  # versiuni pinate (Windows + Python 3.13)
```

### Rulare aplicație

```bash
.venv/Scripts/python main.py    # pornește CLI-ul interactiv
```

### Rulare teste

```bash
.venv/Scripts/python -m pytest tests/ -v                    # toată suita (164)
.venv/Scripts/python -m pytest tests/ --collect-only -q     # listă teste
.venv/Scripts/python -m pytest tests/ -k "ec3"              # doar testele cu "ec3" în nume
```

### Coverage statement + branch pe SUT

```bash
.venv/Scripts/python -m coverage erase
.venv/Scripts/python -m coverage run --branch --source=service.risk_evaluator -m pytest \
    tests/test_risk_evaluator_blackbox.py \
    tests/test_risk_evaluator_whitebox.py \
    tests/test_risk_evaluator_mutation.py
.venv/Scripts/python -m coverage report -m
.venv/Scripts/python -m coverage html -i    # raport HTML în htmlcov/
```

### Mutation testing (PowerShell)

```powershell
$env:PYTHONIOENCODING="utf-8"

# Rulare FINALĂ (toate testele) — așteaptă 35/35 omorâți
$runner = ".venv\Scripts\python.exe -m pytest tests/test_risk_evaluator_blackbox.py tests/test_risk_evaluator_whitebox.py tests/test_risk_evaluator_mutation.py -x -q --no-header"
Remove-Item .mutmut-cache -ErrorAction SilentlyContinue
.venv\Scripts\python.exe -m mutmut run --paths-to-mutate=service/risk_evaluator.py --runner=$runner

# Citire cache (workaround pony bug pe Python 3.13)
.venv\Scripts\python.exe -c "import sqlite3; con = sqlite3.connect('.mutmut-cache'); [print(row) for row in con.execute('SELECT status, COUNT(*) FROM Mutant GROUP BY status')]"
```

Pentru comanda **rulării inițiale** (BB+WB only, fără mutation tests), vezi `documentatie_proiect.md` §21.3.A.

---

## 🛠 Tool-uri folosite

| Tool | Versiune | Rol |
|---|---|---|
| Python | 3.13.2 | Runtime |
| pytest | 9.0.2 | Framework de testare unitară |
| coverage | 7.13.5 | Statement & branch coverage (Ned Batchelder) |
| mutmut | 2.4.5 | Mutation testing |
| pony | 0.7.17 | Dependency mutmut (fixat pentru Python 3.13) |
| draw.io | online | Diagramele (clase, flowchart, CFG, EC partition) |

---

## 🗂 Structura proiectului

```
Proiect_TSS_TESTE/
│
├── domain/                              # Logica de business (clasele principale)
│   ├── __init__.py
│   ├── cargo.py                         # Cargo
│   ├── freight_train.py                 # FreightTrain
│   ├── route.py                         # Route
│   └── transport_plan.py                # TransportPlan (clasa centrală)
│
├── service/                             # Operații pe mai multe entități
│   ├── __init__.py
│   ├── transport_service.py             # TransportService.compare_plans
│   └── risk_evaluator.py                # RiskEvaluator — SUT principal
│
├── exceptions/                          # 9 excepții custom (subclase ValueError)
│   ├── __init__.py
│   └── transport_exceptions.py
│
├── ui/                                  # Interfața utilizator
│   ├── __init__.py
│   └── cli.py                           # CLI interactiv
│
├── tests/                               # 164 teste pytest (toate trec)
│   ├── __init__.py
│   ├── conftest.py                      # 3 fixtures partajate
│   ├── test_cargo_blackbox.py           # 10 teste BB
│   ├── test_freight_train_blackbox.py   # 20 teste BB
│   ├── test_route_blackbox.py           # 27 teste BB
│   ├── test_transport_plan_blackbox.py  # 45 teste BB
│   ├── test_risk_evaluator_blackbox.py  # 23 teste BB pe SUT
│   ├── test_risk_evaluator_whitebox.py  # 36 teste WB pe SUT
│   └── test_risk_evaluator_mutation.py  # 3 teste kill mutanți non-echivalenți
│
├── codAI/                               # Cod generat de Gemini 3.1 Pro + materialele raportului AI
│   ├── blackboxAI.py                    # Suita BB generată automat
│   ├── whiteboxAI.py                    # Suita WB generată automat
│   └── imagini/                         # Capturi prompts + răspunsuri Gemini (4 PNG)
│
├── Diagrame/                            # 4 diagrame draw.io exportate ca PNG
│   ├── diagrama domeniu.png             # Class diagram strat domain
│   ├── Flowchart pentru evaluate_shipment_risk.png
│   ├── Partiționare EC + BVA pentru weight_surcharge.png
│   ├── cfg_evaluate_shipment_risk.png   # CFG pentru SUT
│
├── screenshots/                         # 11 capturi pytest + coverage + mutmut
│   ├── pytest -v.png
│   ├── pytest --collect-only -q.png
│   ├── coverage html report.png
│   ├── coverage terminal output.png
│   ├── mutmut_initial_run.png           # Rulare inițială (BB+WB), 32/3
│   ├── mutmut_initial_sqlite.png
│   ├── mutmut_show_3.png                # Diff mutant #3
│   ├── mutmut_show_6.png                # Diff mutant #6
│   ├── mutmut_show_18.png               # Diff mutant #18
│   ├── mutmut_final_run.png             # Rulare finală, 35/0
│   ├── mutmut_final_sqlite.png
│   └── reportAI/                        # 4 capturi pytest pentru raportul AI
│       ├── bb_run_ai.png
│       ├── bb_run_propriu.png
│       ├── wb_run_ai.png
│       └── wb_run_propriu.png
│
│
├── main.py                              # Entry point CLI
├── .gitignore                           # Exclude .venv, __pycache__, .pytest_cache, .coverage, .mutmut-cache, htmlcov
│
├── README.md                            # Acest fișier
├── documentatie_proiect.md              # 📄 Documentația oficială (~1050 linii) — BB + WB + mutation
├── prezentare.md                        # 🎤 Slide-uri Remark.js (10 slide-uri)
├── prezentare.html                      # Variantă HTML self-contained pentru afișare în browser
├── reportAI.md                          # 🤖 Raport comparativ cu Gemini 3.1 Pro
```

---

## 📋 Strategii aplicate (cerințe T1)

| Cerință T1 | Status | Locație în `documentatie_proiect.md` |
|---|---|---|
| Partiționare clase de echivalență (EC) | ✅ | §4.1, §5.x |
| Analiza valorilor de frontieră (BVA) | ✅ | §4.2, §8.4 |
| Acoperire la nivel de instrucțiune | ✅ 100% | §14 |
| Acoperire la nivel de decizie | ✅ 100% | §15 |
| Acoperire la nivel de condiție | ✅ 100% | §16 |
| Circuite independente (McCabe) | ✅ V(G)=8 | §17 |
| Analiză raport mutanți | ✅ | §22, §23 |
| ≥ 2 teste pentru ≥ 2 mutanți non-echivalenți | ✅ (3 teste / 3 mutanți) | §24 |
| SUT cu ≥3 params, loop, 2 cond (cu/fără else), simplă + compusă | ✅ | §5.5 |

---

## 👥 Contribuții echipă

| Membru | Contribuții principale |
|---|---|
| Marcu George Robert | Implementare cod aplicație, refactor domain/service, WB+mutation, documentație consolidată, integrare tooling, capturi de ecran, demo video |
| Brișiț Mario Vlad | Raport AI tool, Suită teste BB, polish prezentare |

---

## 📚 Index documentație

| Fișier | Conținut |
|---|---|
| **[README.md](README.md)** | Acest fișier — overview rapid | 
| **[documentatie_proiect.md](documentatie_proiect.md)** | Documentația oficială completă (BB+WB+mutation, ~1010 linii) |
| **[prezentare.md](prezentare.md)** | 10 slide-uri Remark.js cu rezumat | 
| **[reportAI.md](reportAI.md)** | Comparație suită manuală vs AI (Gemini 3.1 Pro) | 

---

## 📖 Referințe bibliografice

Vezi `documentatie_proiect.md` §11 pentru lista completă. Surse principale:

1. Predut, S.-N. — *Curs TSS — Functional / Structural / Mutation Testing*, FMI 2024-2026.
2. Pytest, Coverage.py, mutmut — documentații oficiale.

---

## ⚙️ Notă tehnică

Proiectul rulează nativ pe Windows (testat pe Windows 11 Pro, Python 3.13.2). Nu a fost folosită mașină virtuală. Pe Linux/macOS comenzile sunt identice doar că path-ul către Python e `.venv/bin/python` în loc de `.venv/Scripts/python`.


