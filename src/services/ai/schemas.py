from pydantic import BaseModel, Field, model_validator
from typing import List, Optional


class SummarySchema(BaseModel):
    summary: str = ""
    key_points: List[str] = Field(default_factory=list)
    terms: List[str] = Field(default_factory=list)
    conclusion: str = ""

    # Legacy fields AI might use
    overview: Optional[str] = None
    important_terms: Optional[List[str]] = None
    final_takeaway: Optional[str] = None

    @model_validator(mode='before')
    def map_legacy_fields(cls, values):
        if isinstance(values, dict):
            if not values.get("summary") and values.get("overview"):
                values["summary"] = values["overview"]
            if not values.get("terms") and values.get("important_terms"):
                values["terms"] = values["important_terms"]
            if not values.get("conclusion") and values.get("final_takeaway"):
                values["conclusion"] = values["final_takeaway"]
        return values

    class Config:
        extra = "allow"