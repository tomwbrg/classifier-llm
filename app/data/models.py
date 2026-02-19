from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Classification:
    text: str
    category_id: str
    category_name: str
    confidence: float
    reasoning: str
    key_factors: list
    alternative_category: Optional[str] = None
    alternative_category_name: Optional[str] = None
    needs_review: bool = False
    id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class Feedback:
    classif_id: int
    feedback_type: str
    correct_label: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
