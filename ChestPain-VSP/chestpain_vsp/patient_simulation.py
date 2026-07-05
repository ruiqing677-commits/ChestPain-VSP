from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from .evidence_retrieval import retrieve_case_evidence
from .utils import compact_text, get_openai_client, load_env_file


PATIENT_SYSTEM_PROMPT = """You are ChestPain-VSP, a virtual standardized patient for chest-pain consultation training.

Behavior rules:
1. Answer as the patient, not as a doctor, evaluator, or medical record.
2. Stay grounded in the provided case. Do not invent diagnoses, test results, or treatment plans.
3. Use controlled disclosure: answer the question asked; do not reveal hidden high-risk facts unless asked specifically or through a relevant follow-up.
4. If the doctor asks a broad question such as "tell me everything", give a natural brief answer and invite a more specific question.
5. Maintain consistency across repeated questions.
6. Use plain patient language and avoid medical jargon unless the case says the patient knows it.
7. If the doctor asks for emergency red flags or medication history, disclose relevant case facts directly.
"""


class ChestPainVirtualPatient:
    """OpenAI-compatible virtual standardized patient for chest-pain cases."""

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.4,
    ) -> None:
        load_env_file()
        self.model = model or os.environ.get("CHESTPAIN_VSP_MODEL", "gpt-4o")
        self.temperature = temperature
        self._client = get_openai_client(api_key, base_url)

    def build_prompt(self, case_data: Dict[str, Any], question: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        evidence = retrieve_case_evidence(case_data, question)
        patient = case_data.get("patientProfile", {}) or {}
        visible = case_data.get("visible_facts", {}) or {}
        disclosure_policy = case_data.get("disclosure_policy", {}) or {}
        persona_style = case_data.get("persona_style", {}) or {}
        history_lines = []
        for turn in (history or [])[-12:]:
            history_lines.append(f"Doctor: {turn.get('question', '')}")
            history_lines.append(f"Patient: {turn.get('answer', '')}")

        return (
            "[Patient profile]\n"
            f"{json.dumps(patient, ensure_ascii=False, indent=2)}\n\n"
            "[Visible facts]\n"
            f"{json.dumps(visible, ensure_ascii=False, indent=2)}\n\n"
            "[Disclosure policy]\n"
            f"{json.dumps(disclosure_policy, ensure_ascii=False, indent=2)}\n\n"
            "[Persona style]\n"
            f"{json.dumps(persona_style, ensure_ascii=False, indent=2)}\n\n"
            "[Retrieved evidence for the latest question]\n"
            f"{json.dumps(evidence, ensure_ascii=False, indent=2)}\n\n"
            "[Recent dialogue]\n"
            f"{compact_text(history_lines)}\n\n"
            "[Doctor's latest question]\n"
            f"{question}\n\n"
            "Answer as the patient in the same language as the doctor."
        )

    def chat(self, case_data: Dict[str, Any], question: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        messages = [
            {"role": "system", "content": PATIENT_SYSTEM_PROMPT},
            {"role": "user", "content": self.build_prompt(case_data, question, history)},
        ]
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )
        return (response.choices[0].message.content or "").strip()

    def run_script(self, case_data: Dict[str, Any], questions: List[str]) -> Dict[str, Any]:
        history: List[Dict[str, str]] = []
        for question in questions:
            answer = self.chat(case_data, question, history)
            history.append({"question": question, "answer": answer})
        return {"case_id": case_data.get("case_id"), "turns": history}
