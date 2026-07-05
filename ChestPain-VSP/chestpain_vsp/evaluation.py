from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from .utils import get_openai_client, load_env_file


DIMENSIONS = ["QC", "CC", "CD", "RC", "LC", "LN", "CS", "PD"]

DIMENSION_DEFINITIONS = {
    "QC": "Question comprehension: answers the doctor's actual question.",
    "CC": "Case consistency: remains faithful to the reference case.",
    "CD": "Controlled disclosure: avoids over-disclosure and reveals details when appropriately asked.",
    "RC": "Response completeness: sufficiently addresses targeted clinically relevant facts.",
    "LC": "Logical coherence: internally coherent and clinically sensible patient utterances.",
    "LN": "Language naturalness: sounds like a natural patient, not a system dump.",
    "CS": "Clinical safety: avoids unsafe advice, false reassurance, or misleading clinical claims.",
    "PD": "Patient-doctor interaction: appropriate patient-like tone and cooperation.",
}


JUDGE_SYSTEM_PROMPT = """You are an expert evaluator of virtual standardized patients in chest-pain consultations.
Score the generated patient dialogue against the reference case on eight dimensions.

Scoring scale for each dimension:
1 = poor, 2 = weak, 3 = acceptable, 4 = good, 5 = excellent.

Return strict JSON:
{
  "scores": {"QC": 1-5, "CC": 1-5, "CD": 1-5, "RC": 1-5, "LC": 1-5, "LN": 1-5, "CS": 1-5, "PD": 1-5},
  "reasons": {"QC": "...", ...},
  "overall_summary": "..."
}
"""


def compute_vpq_score_100(scores: Dict[str, int | float]) -> float:
    return round(sum(float(scores.get(name, 0)) for name in DIMENSIONS) / len(DIMENSIONS) * 20, 2)


class ChestPainVPQEvaluator:
    """LLM-backed VPQ evaluator."""

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.0,
    ) -> None:
        load_env_file()
        self.model = model or os.environ.get("CHESTPAIN_VSP_JUDGE_MODEL") or os.environ.get("CHESTPAIN_VSP_MODEL", "gpt-4o")
        self.temperature = temperature
        self._client = get_openai_client(api_key, base_url)

    def evaluate(self, dialogue: Dict[str, Any], case_reference: Dict[str, Any], script_spec: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {
            "dimension_definitions": DIMENSION_DEFINITIONS,
            "case_reference": case_reference,
            "script_spec": script_spec or {},
            "dialogue": dialogue,
        }
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            temperature=self.temperature,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        result = json.loads(content)
        scores = result.get("scores", {})
        result["vpq_score_100"] = compute_vpq_score_100(scores)
        return result
