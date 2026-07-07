from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

from .evidence_retrieval import infer_intent_from_question
from .utils import get_llm_client, load_env_file


INTENT_CATEGORIES = [
    "pain_features",
    "red_flags",
    "risk_history",
    "benign_alternative_clues",
    "evidence_requests",
    "reasoning_disposition",
    "other_unclear",
]


INTENT_PROMPT = """You are a chest-pain clinical intent classifier.
Classify the doctor's latest utterance into exactly one category:

- pain_features: onset, location, duration, character, radiation, severity, aggravating/relieving factors
- red_flags: dyspnea, sweating, syncope, hemoptysis, neurological deficits, shock, severe tearing pain
- risk_history: cardiovascular risk factors, past history, medication use, family history, lifestyle risks
- benign_alternative_clues: reflux, musculoskeletal clues, anxiety, pleuritic or positional clues
- evidence_requests: ECG, troponin, D-dimer, imaging, labs, physical exam, vital signs
- reasoning_disposition: diagnosis, risk stratification, triage, admission, discharge, treatment plan
- other_unclear: greetings, vague statements, or anything not classifiable above

Return strict JSON: {"intent": "...", "rationale": "..."}.
"""


class ChestPainIntentRecognizer:
    """LLM-backed chest-pain intent recognizer with a deterministic fallback."""

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.0,
        use_llm: bool = True,
    ) -> None:
        load_env_file()
        self.model = model or os.environ.get("CHESTPAIN_VSP_INTENT_MODEL") or os.environ.get("CHESTPAIN_VSP_MODEL", "your_model_name")
        self.temperature = temperature
        self.use_llm = use_llm
        self._client = get_llm_client(api_key, base_url) if use_llm else None

    def recognize(self, question: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, str]:
        if not self.use_llm:
            intent = infer_intent_from_question(question)
            return {"intent": intent, "rationale": "Keyword-based fallback."}

        messages = [
            {"role": "system", "content": INTENT_PROMPT},
            {
                "role": "user",
                "content": json.dumps({"history": history or [], "latest_question": question}, ensure_ascii=False),
            },
        ]
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        intent = data.get("intent", "other_unclear")
        if intent not in INTENT_CATEGORIES:
            intent = "other_unclear"
        return {"intent": intent, "rationale": data.get("rationale", "")}
