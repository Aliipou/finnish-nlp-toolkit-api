"""
Profanity Detection Router
Handles profanity/toxicity detection endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import ProfanityRequest, ProfanityResponse
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

# Initialize profanity detector (advanced if configured, basic otherwise)
try:
    if settings.USE_TRANSFORMERS:
        from app.services.advanced_profanity_model import AdvancedProfanityDetector
        profanity_detector = AdvancedProfanityDetector(use_transformers=True)
        logger.info("Using Advanced Profanity Detector with Transformers")
    else:
        from app.services.profanity_model import ProfanityDetector
        profanity_detector = ProfanityDetector()
        logger.info("Using Basic Profanity Detector")
except Exception as e:
    logger.error(f"Failed to initialize profanity detector: {e}")
    # Fallback to basic
    from app.services.profanity_model import ProfanityDetector
    profanity_detector = ProfanityDetector()
    logger.warning("Fallback to Basic Profanity Detector")


@router.post("/swear-check", response_model=ProfanityResponse)
async def check_profanity(request: ProfanityRequest):
    """
    Check Finnish text for profanity/toxicity

    **Input:**
    - text: Text to check
    - return_flagged_words: Return list of flagged words
    - threshold: Detection threshold (0-1)

    **Output:**
    - Toxicity score
    - Is toxic boolean
    - Flagged words (if requested)
    - Severity rating
    """
    if profanity_detector is None:
        raise HTTPException(status_code=503, detail="Profanity detector service not available")

    try:
        result = profanity_detector.detect(
            text=request.text,
            return_flagged_words=request.return_flagged_words,
            threshold=request.threshold
        )
        return result
    except Exception as e:
        logger.error(f"Profanity detection error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Profanity detection failed: {str(e)}")


@router.get("/swear-check", response_model=ProfanityResponse)
async def check_profanity_get(
    text: str = Query(..., description="Text to check for profanity", min_length=1, max_length=10000),
    return_flagged_words: bool = Query(False, description="Return list of flagged words"),
    threshold: float = Query(0.5, description="Detection threshold (0-1)", ge=0.0, le=1.0)
):
    """
    Check Finnish text for profanity/toxicity (GET method)

    **Parameters:**
    - text: Text to check
    - return_flagged_words: Return list of flagged words
    - threshold: Detection threshold

    **Returns:**
    - Profanity detection results
    """
    request = ProfanityRequest(
        text=text,
        return_flagged_words=return_flagged_words,
        threshold=threshold
    )
    return await check_profanity(request)
