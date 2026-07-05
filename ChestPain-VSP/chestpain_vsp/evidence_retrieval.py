from __future__ import annotations

import re
from typing import Any, Dict, List

from .utils import compact_text, dedupe_keep_order


INTENT_KEYWORDS = {
    "pain_features": ["pain", "chest", "location", "duration", "radiat", "疼", "胸痛", "位置", "多久", "放射"],
    "red_flags": ["sweat", "syncope", "dyspnea", "hemoptysis", "大汗", "晕厥", "气短", "咯血", "危险"],
    "risk_history": ["hypertension", "diabetes", "smok", "family", "history", "高血压", "糖尿病", "吸烟", "家族", "病史"],
    "medications": ["medicine", "drug", "aspirin", "nitro", "medication", "药", "阿司匹林", "硝酸"],
    "benign_alternative": ["reflux", "press", "palpation", "food", "muscle", "反酸", "按压", "体位", "肌肉"],
    "evidence_request": ["ecg", "troponin", "d-dimer", "x-ray", "心电图", "肌钙蛋白", "检查", "化验"],
}


CASE_FIELD_GROUPS = {
    "pain_features": ["chief_complaint", "pain_location", "pain_duration", "pain_character", "symptoms"],
    "red_flags": ["red_flags", "associated_symptoms", "relevant_negatives"],
    "risk_history": ["risk_factors", "past_medical_history", "personal_history", "family_history"],
    "medications": ["medications", "recent_self_medication", "other_medical_history"],
    "benign_alternative": ["contextual_clues", "diagnostic_clues", "relevant_negatives"],
    "evidence_request": ["minimum_safe_actions", "template", "reasoning_graph"],
}


def infer_intent_from_question(question: str) -> str:
    normalized = question.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword.lower() in normalized for keyword in keywords):
            return intent
    return "other"


def _walk_case(case_data: Dict[str, Any], field_name: str) -> List[str]:
    matches: List[str] = []

    def visit(value: Any, key: str = "") -> None:
        if key == field_name:
            text = compact_text(value)
            if text:
                matches.append(text)
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                visit(child_value, child_key)
        elif isinstance(value, list):
            for child_value in value:
                visit(child_value, key)

    visit(case_data)
    return matches


def retrieve_case_evidence(case_data: Dict[str, Any], question: str, intent: str | None = None, top_k: int = 8) -> Dict[str, Any]:
    """Retrieve a compact evidence bundle from a structured chest-pain case.

    This is intentionally deterministic and lightweight. It supports the
    controlled-disclosure logic used by ChestPain-VSP without requiring a
    vector database in the public release.
    """
    resolved_intent = intent or infer_intent_from_question(question)
    field_names = CASE_FIELD_GROUPS.get(resolved_intent, [])
    evidence: List[str] = []
    for field_name in field_names:
        evidence.extend(_walk_case(case_data, field_name))

    if not evidence:
        patient = case_data.get("patientProfile", {}) or {}
        visible = case_data.get("visible_facts", {}) or {}
        evidence.extend([compact_text(patient.get("chief_complaint")), compact_text(visible)])

    return {
        "intent": resolved_intent,
        "evidence": dedupe_keep_order(evidence)[:top_k],
        "question": question,
    }
