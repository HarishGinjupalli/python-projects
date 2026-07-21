# Client Effort Estimator & Proposal Automation Tool

A Python-based consulting utility that turns raw client requirements into a
costed effort estimate and a client-ready Word proposal — the kind of workflow
a delivery/consulting analyst runs before a statement of work goes out.

## Why this project exists

Consulting engagements (the type Infosys' Enterprise Package Application
Services teams run) live and die on three things:

1. **Accurate effort estimation** — translating requirements into person-days
2. **Defensible pricing** — applying a rate card + complexity + risk buffer in
   a way that's consistent and auditable
3. **Fast, professional proposal turnaround** — not re-typing the same Word
   document structure every time

This tool automates all three, driven entirely by config files (YAML), so
rate cards, complexity multipliers, and risk buffers can be updated without
touching code — a lightweight configuration-management pattern.

## Features

- **Config-driven rate card** (`config/rate_card.yaml`): role-wise daily
  rates, currency, complexity multipliers, risk contingency %
- **Effort estimation engine** (`src/estimator.py`): reads client
  requirements (CSV), computes person-days per requirement based on
  complexity and role mix, applies risk buffer, rolls up to a total estimate
- **Cost calculation**: person-days × rate card → line-item and total cost,
  with currency formatting
- **Proposal generation** (`src/proposal_generator.py`): builds a formatted
  Word (.docx) proposal — cover section, scope table, effort & cost
  breakdown table, assumptions, and terms — using `python-docx`
- **CLI** (`main.py`): single command from CSV input to finished `.docx`
- **Config validation**: guards against malformed rate cards / missing roles
  before any estimate is generated
- **Logging**: structured run log written to `output/run.log`
- **Unit tests** (`pytest`): covers estimator math, config validation, and
  edge cases (unknown role, zero requirements, negative values)

## Project structure

```
project-effort-estimator/
├── README.md
├── requirements.txt
├── .gitignore
├── main.py                        # CLI entry point
├── config/
│   ├── rate_card.yaml             # roles, daily rates, multipliers, buffer
│   └── config.yaml                # company info, currency, output paths
├── data/
│   └── sample_client_requirements.csv
├── src/
│   ├── __init__.py
│   ├── config_manager.py          # loads + validates YAML config
│   ├── estimator.py                # effort & cost calculation engine
│   ├── proposal_generator.py       # builds the Word proposal
│   └── utils.py                    # logging setup, helpers
├── tests/
│   ├── __init__.py
│   ├── test_config_manager.py
│   └── test_estimator.py
└── output/                         # generated proposals + logs land here
```

## Setup (Windows / VS Code)

```powershell
# from the project root, in a VS Code terminal
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```powershell
python main.py --input data/sample_client_requirements.csv --client "Contoso Retail" --output output/Contoso_Proposal.docx
```

Run the test suite:

```powershell
pytest tests/ -v
   vscode
python -m pytest tests -v
```

## Sample workflow

1. Client shares a requirements list → saved as CSV (`data/sample_client_requirements.csv`)
2. `estimator.py` maps each requirement to a role + complexity, computes
   person-days, applies the risk buffer from `rate_card.yaml`
3. `proposal_generator.py` renders everything into a Word document with a
   scope table and a cost summary table
4. Output lands in `output/`, ready to send to the client

## Configuration example

`config/rate_card.yaml` defines roles like:

```yaml
roles:
  Python Developer: 8000
  Senior Consultant: 14000
  Business Analyst: 9500
complexity_multiplier:
  Low: 1.0
  Medium: 1.5
  High: 2.2
risk_buffer_percent: 12
currency: INR
```

Change rates, add roles, or adjust the risk buffer without touching a single
line of Python — this is the "software configuration management" pattern
referenced in enterprise consulting workflows.

## Possible extensions

- REST API wrapper (FastAPI) so estimates can be requested by a front-end
- Multi-currency support with live FX rates
- PDF export alongside Word
- Historical estimate tracking (SQLite) to compare estimated vs. actual effort

