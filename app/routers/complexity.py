"""
Complexity Analysis Router
Handles sentence complexity analysis endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import ComplexityRequest, ComplexityResponse
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

# Initialize complexity engine (advanced if configured, basic otherwise)
try:
    if settings.USE_UDPIPE or settings.USE_SPACY:
        from app.services.advanced_complexity_engine import AdvancedComplexityEngine
        complexity_analyzer = AdvancedComplexityEngine(
            use_udpipe=settings.USE_UDPIPE,
            use_spacy=settings.USE_SPACY
        )
        logger.info(f"Using Advanced Complexity Analyzer (UDPipe: {settings.USE_UDPIPE}, spaCy: {settings.USE_SPACY})")
    else:
        from app.services.complexity_engine import ComplexityEngine
        complexity_analyzer = ComplexityEngine()
        logger.info("Using Basic Complexity Analyzer")
except Exception as e:
    logger.error(f"Failed to initialize complexity analyzer: {e}")
    # Fallback to basic
    from app.services.complexity_engine import ComplexityEngine
    complexity_analyzer = ComplexityEngine()
    logger.warning("Fallback to Basic Complexity Analyzer")


@router.post("/complexity", response_model=ComplexityResponse)
async def analyze_complexity(request: ComplexityRequest):
    """
    Analyze Finnish text complexity

    **Input:**
    - text: Finnish text to analyze
    - detailed: Include detailed metrics

    **Output:**
    - Sentence count
    - Word count
    - Clause count
    - Morphological depth score
    - Case distribution
    - Complexity rating
    """
    if complexity_analyzer is None:
        raise HTTPException(status_code=503, detail="Complexity analyzer service not available")

    try:
        result = complexity_analyzer.analyze(
            text=request.text,
            detailed=request.detailed
        )
        return result
    except Exception as e:
        logger.error(f"Complexity analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Complexity analysis failed: {str(e)}")


@router.get("/complexity", response_model=ComplexityResponse)
async def analyze_complexity_get(
    text: str = Query(..., description="Finnish text to analyze", min_length=1, max_length=10000),
    detailed: bool = Query(True, description="Include detailed analysis")
):
    """
    Analyze Finnish text complexity (GET method)

    **Parameters:**
    - text: Finnish text to analyze
    - detailed: Include detailed metrics

    **Returns:**
    - Complexity analysis results
    """
    request = ComplexityRequest(text=text, detailed=detailed)
    return await analyze_complexity(request)
