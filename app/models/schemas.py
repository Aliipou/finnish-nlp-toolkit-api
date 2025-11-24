"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional


# Lemmatization Models
class LemmatizationRequest(BaseModel):
    text: str = Field(..., description="Finnish text to lemmatize", min_length=1, max_length=10000)
    include_morphology: bool = Field(default=True, description="Include morphological information")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Kissani söi hiiret nopeasti",
                "include_morphology": True
            }
        }


class WordLemma(BaseModel):
    original: str = Field(..., description="Original word form")
    lemma: str = Field(..., description="Base form (lemma)")
    pos: Optional[str] = Field(None, description="Part of speech")
    morphology: Optional[Dict[str, str]] = Field(None, description="Morphological features")


class LemmatizationResponse(BaseModel):
    text: str = Field(..., description="Original input text")
    lemmas: List[WordLemma] = Field(..., description="List of lemmatized words")
    word_count: int = Field(..., description="Number of words processed")


# Complexity Analysis Models
class ComplexityRequest(BaseModel):
    text: str = Field(..., description="Finnish text to analyze", min_length=1, max_length=10000)
    detailed: bool = Field(default=True, description="Include detailed analysis")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Kissa, joka söi hiiren, juoksi nopeasti puutarhaan.",
                "detailed": True
            }
        }


class CaseDistribution(BaseModel):
    nominative: int = 0
    genitive: int = 0
    partitive: int = 0
    inessive: int = 0
    elative: int = 0
    illative: int = 0
    adessive: int = 0
    ablative: int = 0
    allative: int = 0
    essive: int = 0
    translative: int = 0
    other: int = 0


class ComplexityResponse(BaseModel):
    text: str = Field(..., description="Original input text")
    sentence_count: int = Field(..., description="Number of sentences")
    word_count: int = Field(..., description="Number of words")
    clause_count: int = Field(..., description="Number of clauses detected")
    morphological_depth_score: float = Field(..., description="Complexity score based on morphology (0-100)")
    average_word_length: float = Field(..., description="Average word length in characters")
    case_distribution: Optional[CaseDistribution] = Field(None, description="Distribution of grammatical cases")
    complexity_rating: str = Field(..., description="Simple, Moderate, or Complex")


# Profanity Detection Models
class ProfanityRequest(BaseModel):
    text: str = Field(..., description="Text to check for profanity", min_length=1, max_length=10000)
    return_flagged_words: bool = Field(default=False, description="Return list of flagged words")
    threshold: float = Field(default=0.5, description="Detection threshold (0-1)", ge=0.0, le=1.0)

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Tämä on testi teksti",
                "return_flagged_words": True,
                "threshold": 0.5
            }
        }


class FlaggedWord(BaseModel):
    word: str = Field(..., description="Flagged word")
    position: int = Field(..., description="Position in text")
    confidence: float = Field(..., description="Confidence score (0-1)")


class ProfanityResponse(BaseModel):
    text: str = Field(..., description="Original input text")
    is_toxic: bool = Field(..., description="Whether text contains profanity/toxicity")
    toxicity_score: float = Field(..., description="Overall toxicity probability (0-1)")
    flagged_words: Optional[List[FlaggedWord]] = Field(None, description="List of flagged words if requested")
    severity: str = Field(..., description="None, Low, Medium, or High")


# Error Response Model
class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
