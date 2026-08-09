"""
Transformation log — ensures reproducibility.
"""
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class TransformationRecord:
    step: int
    column: str
    action: str
    before: Optional[str]
    after: Optional[str]
    rows_affected: int
    details: Optional[str] = None

    def to_dict(self):
        return {
            "step": self.step,
            "column": self.column,
            "action": self.action,
            "before": self.before,
            "after": self.after,
            "rows_affected": self.rows_affected,
            "details": self.details
        }
