# ChestPain-VSP Benchmark Examples

This directory contains a minimal public benchmark example for ChestPain-VSP.
It follows the same structure used in the experiments, but only includes a few
de-identified synthetic examples. Full private evaluation cases and paper
outputs are not included in this anonymous repository.

## Layout

```text
benchmark/
├── README.md
├── example_cases/
│   ├── 001.json
│   ├── 002.json
│   └── 003.json
└── scripts/
    ├── S1_standard.json
    ├── S2_disclosure.json
    └── S3_consistency.json
```

## Case Format

Each case is a structured JSON file with:

- `case_id`
- `category`
- `risk_level`
- `patientProfile`
- `visible_facts`
- `hidden_facts`
- `disclosure_policy`
- `persona_style`

The patient simulator should use `visible_facts` for initial answers and reveal
`hidden_facts` only when the doctor's question asks for the relevant intent.

## Scripts

- `S1_standard.json`: standard history-taking coverage.
- `S2_disclosure.json`: stress test for avoiding over-disclosure.
- `S3_consistency.json`: repeated-question consistency test.

The scripts can be loaded directly:

```python
from chestpain_vsp.utils import read_json

case_data = read_json("benchmark/example_cases/001.json")
script = read_json("benchmark/scripts/S1_standard.json")
```
