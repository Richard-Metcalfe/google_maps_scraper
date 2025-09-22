from dataclasses import dataclass


@dataclass
class Organisation:
    organisation_name: str = None
    organisation_location: str = None
    contact_number: str = None
    website: str = None
    average_review_count: int = None
    average_review_points: float = None
