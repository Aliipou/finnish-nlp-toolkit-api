"""
Batch Processing Router
Handle multiple texts in a single request
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from app.models.schemas import LemmatizationResponse, ComplexityResponse, ProfanityResponse
from app.services.lemma_engine import LemmatizerEngine
from app.services.complexity_engine import ComplexityEngine
from app.services.profanity_model import ProfanityDetector
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize engines
try:
    lemmatizer = LemmatizerEngine()
    complexity_analyzer = ComplexityEngine()
    profanity_detector = ProfanityDetector()
except Exception as e:
    logger.error(f"Failed to initialize engines: {e}")


# Batch request models
class BatchLemmatizeRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to lemmatize", min_items=1, max_items=100)
    include_morphology: bool = Field(default=True, description="Include morphological information")


class BatchComplexityRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to analyze", min_items=1, max_items=100)
    detailed: bool = Field(default=True, description="Include detailed analysis")


class BatchProfanityRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to check", min_items=1, max_items=100)
    return_flagged_words: bool = Field(default=False, description="Return flagged words")
    threshold: float = Field(default=0.5, description="Detection threshold", ge=0.0, le=1.0)


# Batch response models
class BatchLemmatizeResponse(BaseModel):
    results: List[LemmatizationResponse]
    total_texts: int
    total_words: int


class BatchComplexityResponse(BaseModel):
    results: List[ComplexityResponse]
    total_texts: int
    average_complexity_score: float


class BatchProfanityResponse(BaseModel):
    results: List[ProfanityResponse]
    total_texts: int
    toxic_count: int
    average_toxicity_score: float


@router.post("/batch/lemmatize", response_model=BatchLemmatizeResponse)
async def batch_lemmatize(request: BatchLemmatizeRequest):
    """
    Batch lemmatization of multiple texts

    **Input:**
    - texts: List of Finnish texts to lemmatize (max 100)
    - include_morphology: Include morphological features

    **Output:**
    - List of lemmatization results
    - Total statistics
    """
    try:
        results = []
        total_words = 0

        for text in request.texts:
            result = lemmatizer.lemmatize(
                text=text,
                include_morphology=request.include_morphology
            )
            results.append(result)
            total_words += result.word_count

        return BatchLemmatizeResponse(
            results=results,
            total_texts=len(results),
            total_words=total_words
        )

    except Exception as e:
        logger.error(f"Batch lemmatization error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch lemmatization failed: {str(e)}")


@router.post("/batch/complexity", response_model=BatchComplexityResponse)
async def batch_complexity(request: BatchComplexityRequest):
    """
    Batch complexity analysis of multiple texts

    **Input:**
    - texts: List of texts to analyze (max 100)
    - detailed: Include detailed metrics

    **Output:**
    - List of complexity results
    - Average complexity score
    """
    try:
        results = []
        total_score = 0.0

        for text in request.texts:
            result = complexity_analyzer.analyze(
                text=text,
                detailed=request.detailed
            )
            results.append(result)
            total_score += result.morphological_depth_score

        avg_score = total_score / len(results) if results else 0.0

        return BatchComplexityResponse(
            results=results,
            total_texts=len(results),
            average_complexity_score=round(avg_score, 2)
        )

    except Exception as e:
        logger.error(f"Batch complexity error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch complexity analysis failed: {str(e)}")


@router.post("/batch/swear-check", response_model=BatchProfanityResponse)
async def batch_profanity(request: BatchProfanityRequest):
    """
    Batch profanity detection for multiple texts

    **Input:**
    - texts: List of texts to check (max 100)
    - return_flagged_words: Return flagged words
    - threshold: Detection threshold

    **Output:**
    - List of profanity detection results
    - Total toxic count
    - Average toxicity score
    """
    try:
        results = []
        toxic_count = 0
        total_score = 0.0

        for text in request.texts:
            result = profanity_detector.detect(
                text=text,
                return_flagged_words=request.return_flagged_words,
                threshold=request.threshold
            )
            results.append(result)

            if result.is_toxic:
                toxic_count += 1
            total_score += result.toxicity_score

        avg_score = total_score / len(results) if results else 0.0

        return BatchProfanityResponse(
            results=results,
            total_texts=len(results),
            toxic_count=toxic_count,
            average_toxicity_score=round(avg_score, 3)
        )

    except Exception as e:
        logger.error(f"Batch profanity detection error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch profanity detection failed: {str(e)}")
