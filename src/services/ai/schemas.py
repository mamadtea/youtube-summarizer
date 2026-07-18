from pydantic import BaseModel, Field
from typing import List



class SummarySchema(BaseModel):

    overview: str = ""

    key_points: List[str] = Field(
        default_factory=list
    )

    important_terms: List[str] = Field(
        default_factory=list
    )

    tools: List[str] = Field(
        default_factory=list
    )

    resources: List[str] = Field(
        default_factory=list
    )
    
    tags: List[str] = Field(
        default_factory=list
    )



    final_takeaway: str = ""



    class Config:
        extra = "ignore"