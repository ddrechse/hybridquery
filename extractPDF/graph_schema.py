from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class Treatment(BaseModel):
    """A pharmaceutical treatment, therapy, or medication mentioned in the text."""
    name: str = Field(description="The generic or brand name of the treatment or medication (e.g. 'Metformin', 'GLP-1 Agonists').")
    type: Literal["Pharmaceutical", "Lifestyle", "Surgery", "Other"] = Field(
        default="Pharmaceutical", 
        description="The category of the treatment."
    )

class Condition(BaseModel):
    """A medical condition, disease, or symptom."""
    name: str = Field(description="The name of the condition or disease (e.g. 'Type 2 Diabetes', 'Hypertension').")

class Relationship(BaseModel):
    """A relationship between a treatment and a condition."""
    treatment_name: str = Field(description="Name of the treatment, must match a Treatment name exactly.")
    condition_name: str = Field(description="Name of the condition, must match a Condition name exactly.")
    relationship_type: Literal["TREATS", "CAUSES", "PREVENTS"] = Field(
        default="TREATS",
        description="The type of relationship. Use TREATS if the treatment is used for the condition."
    )
    confidence: float = Field(description="Confidence score between 0.0 and 1.0", ge=0.0, le=1.0)

class ExtractionResult(BaseModel):
    """The complete result of extracting medical graph data from text."""
    treatments: List[Treatment] = Field(default_factory=list, description="List of unique treatments mentioned.")
    conditions: List[Condition] = Field(default_factory=list, description="List of unique conditions mentioned.")
    relationships: List[Relationship] = Field(default_factory=list, description="List of relationships found between treatments and conditions.")
