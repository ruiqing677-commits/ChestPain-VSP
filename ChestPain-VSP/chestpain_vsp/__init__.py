"""ChestPain-VSP public research package.

This package provides lightweight, OpenAI-compatible components for
chest-pain virtual standardized patient simulation, intent recognition,
case-grounded evidence retrieval, and VPQ-style evaluation.
"""

from .patient_simulation import ChestPainVirtualPatient
from .intent_recognition import ChestPainIntentRecognizer
from .evidence_retrieval import retrieve_case_evidence
from .evaluation import ChestPainVPQEvaluator, compute_vpq_score_100

__all__ = [
    "ChestPainVirtualPatient",
    "ChestPainIntentRecognizer",
    "retrieve_case_evidence",
    "ChestPainVPQEvaluator",
    "compute_vpq_score_100",
]
