# ChestPain-VSP

ChestPain-VSP is a research-oriented virtual standardized patient framework for
chest-pain consultation training and evaluation. It provides lightweight modules
for case-grounded patient simulation, chest-pain intent recognition, deterministic
case-evidence retrieval, and VPQ-style dialogue quality evaluation.

This anonymous repository contains public code, synthetic de-identified-style
benchmark examples, and supplementary intent-classification materials for paper
review. Full experimental outputs, generated dialogues, evaluation JSON files,
API keys, and complete private evaluation data are not included.

## Repository Structure

```text
ChestPain-VSP/
├── README.md
├── LICENSE
├── requirements.txt
├── .env.example
├── .gitignore
│
├── chestpain_vsp/
│   ├── __init__.py
│   ├── patient_simulation.py
│   ├── intent_recognition.py
│   ├── evidence_retrieval.py
│   ├── evaluation.py
│   └── utils.py
│
├── benchmark/
│   ├── README.md
│   ├── example_cases/
│   │   ├── 001.json
│   │   ├── 002.json
│   │   └── 003.json
│   └── consultation_scripts/
│       ├── S1_standard.json
│       ├── S2_disclosure.json
│       └── S3_consistency.json
│
└── supplementary/
    └── intent_classification/
        ├── README.md
        ├── intent_label_definitions.md
        ├── category_level_results.csv
        └── intent_examples.md
```

## Highlights

- Chest-pain-specific virtual patient simulation.
- Controlled disclosure of hidden case facts.
- Intent-aware evidence retrieval from structured patient cases.
- VPQ evaluation across eight patient-quality dimensions.
- Configurable LLM API support.
- Public example cases, standardized consultation scripts, and intent-classification supplement.

## Installation

```bash
git clone <anonymous-repository-url>
cd ChestPain-VSP
pip install -r requirements.txt
```

## API Configuration

Copy the environment template and fill in your own LLM API credentials:

```bash
cp .env.example .env
```

The `.env` file must never be committed.

```bash
CHESTPAIN_VSP_API_KEY=your_api_key_here
CHESTPAIN_VSP_BASE_URL=https://api.example.com/v1
CHESTPAIN_VSP_MODEL=your_model_name
CHESTPAIN_VSP_INTENT_MODEL=your_intent_model_name
CHESTPAIN_VSP_JUDGE_MODEL=your_judge_model_name
```

## API-based Quick Example

```python
from chestpain_vsp import ChestPainVirtualPatient
from chestpain_vsp.utils import read_json

case_data = read_json("benchmark/example_cases/001.json")
script = read_json("benchmark/consultation_scripts/S1_standard.json")

patient = ChestPainVirtualPatient()
dialogue = patient.run_script(case_data, script["questions"])
print(dialogue)
```

## Benchmark Examples

The `benchmark/` directory contains:

- `example_cases/`: small synthetic de-identified-style chest-pain cases.
- `consultation_scripts/S1_standard.json`: standard chest-pain history-taking script.
- `consultation_scripts/S2_disclosure.json`: controlled-disclosure stress test.
- `consultation_scripts/S3_consistency.json`: conversational consistency stress test.

These files document the expected data format and standardized consultation-script format. They are not the full private evaluation set.

## Intent Classification Supplement

The `supplementary/intent_classification/` directory provides category-level
intent-classification results, label definitions, and representative utterance
examples corresponding to the supplementary statement in the paper.

## Evaluation Dimensions

VPQ evaluation uses eight dimensions:

| Abbrev. | Meaning |
|---|---|
| QC | Question comprehension |
| CC | Case consistency |
| CD | Controlled disclosure |
| RC | Response completeness |
| LC | Logical coherence |
| LN | Language naturalness |
| CS | Clinical safety |
| PD | Patient-doctor interaction |

## What Is Not Included

This repository intentionally excludes:

- generated dialogues
- evaluation JSON files
- experiment logs
- result tables from private evaluation runs
- API keys or private endpoints
- complete private evaluation data
- server paths or local machine metadata

## Citation

Citation information will be added after the anonymous review period.
