from dataclasses import dataclass, field

from typing import Optional, Dict, Any


@dataclass
class PatientState:
    # Demographics
    age: Optional[int] = None
    sex: Optional[str] = None  # "male"/"female"
    # Risk factors
    diabetes: Optional[bool] = None
    hypertension: Optional[bool] = None
    dyslipidaemia: Optional[bool] = None
    smoking: Optional[bool] = None
    # Chest-pain criteria
    loc_pos: Optional[bool] = None
    trg_pos: Optional[bool] = None
    rlf_pos: Optional[bool] = None
    # Derived
    chest_pain_type: Optional[str] = None
    # Control
    confirmed_safety: Optional[bool] = None
    result: Optional[float] = None
    notes: Dict[str, Any] = field(default_factory=dict)
