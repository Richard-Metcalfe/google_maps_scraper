from dataclasses import dataclass
from typing import Optional

@dataclass
class Organisation:
    organisation_name: Optional[str] = None
    organisation_location: Optional[str] = None
    contact_number: Optional[str] = None
    website: Optional[str] = None
    average_review_count: int = 0
    average_review_points: float = 0.0
    email: Optional[str] = None
