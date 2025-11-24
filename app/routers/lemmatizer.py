"""
Lemmatization Router
Handles Finnish text lemmatization endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import LemmatizationRequest, LemmatizationResponse
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

# Initialize lemmatizer engine (advanced if configured, basic otherwise)
try:
    if settings.USE_VOIKKO:
        from app.services.advanced_lemma_engine import AdvancedLemmatizerEngine
        lemmatizer = AdvancedLemmatizerEngine(use_voikko=True)
        logger.info("Using Advanced Lemmatizer with Voikko")
    else:
        from app.services.lemma_engine import LemmatizerEngine
        lemmatizer = LemmatizerEngine()
        logger.info("Using Basic Lemmatizer")
except Exception as e:
    logger.error(f"Failed to initialize lemmatizer: {e}")
    # Fallback to basic
    from app.services.lemma_engine import LemmatizerEngine
    lemmatizer = LemmatizerEngine()
    logger.warning("Fallback to Basic Lemmatizer")


@router.post("/lemmatize", response_model=LemmatizationResponse)
async def lemmatize_text(request: LemmatizationRequest):
    """
    Lemmatize Finnish text

    **Input:**
    - text: Finnish text to lemmatize
    - include_morphology: Whether to include morphological features

    **Output:**
    - Original text
    - List of lemmatized words with morphological information
    - Word count
    """
    if lemmatizer is None:
        raise HTTPException(status_code=503, detail="Lemmatizer service not available")

    try:
        result = lemmatizer.lemmatize(
            text=request.text,
            include_morphology=request.include_morphology
        )
        return result
    except Exception as e:
        logger.error(f"Lemmatization error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lemmatization failed: {str(e)}")


@router.get("/lemmatize", response_model=LemmatizationResponse)
async def lemmatize_text_get(
    text: str = Query(..., description="Finnish text to lemmatize", min_length=1, max_length=10000),
    include_morphology: bool = Query(True, description="Include morphological information")
):
    """
    Lemmatize Finnish text (GET method for simple queries)

    **Parameters:**
    - text: Finnish text to lemmatize
    - include_morphology: Whether to include morphological features

    **Returns:**
    - Lemmatization results
    """
    request = LemmatizationRequest(text=text, include_morphology=include_morphology)
    return await lemmatize_text(request)
