"""
Advanced Finnish Profanity/Toxicity Detection
ML-based detection using transformers (FinBERT) with keyword fallback
"""
import re
import logging
from typing import List, Optional
from app.models.schemas import ProfanityResponse, FlaggedWord

logger = logging.getLogger(__name__)


class AdvancedProfanityDetector:
    """
    Production-grade toxicity detector using FinBERT or fallback to keywords
    """

    def __init__(self, use_transformers: bool = True):
        """
        Initialize advanced profanity detector

        Args:
            use_transformers: Try to use FinBERT transformer model
        """
        logger.info("Initializing Advanced Profanity Detection Model")

        self.model = None
        self.tokenizer = None
        self.use_transformers = use_transformers

        # Try to load transformer model
        if use_transformers:
            try:
                from transformers import AutoTokenizer, AutoModelForSequenceClassification
                import torch

                # Try to load FinBERT-based toxicity model
                # Note: You would need to train or download a toxicity classification model
                # For now, we'll use FinBERT base and show the structure
                model_name = "TurkuNLP/bert-base-finnish-cased-v1"

                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                    # In production, this would be a fine-tuned toxicity model
                    # self.model = AutoModelForSequenceClassification.from_pretrained("path/to/toxicity-model")
                    logger.info("✅ Transformer tokenizer loaded")
                    logger.warning("⚠️  Full toxicity model not loaded - using keyword fallback")
                    logger.warning("To use ML model, train on Finnish toxicity dataset")
                    self.model = None  # Set to None since we don't have trained model
                except Exception as e:
                    logger.warning(f"⚠️  Could not load transformer model: {e}")
                    self.model = None
                    self.tokenizer = None

            except ImportError:
                logger.warning("⚠️  transformers library not available")
                logger.warning("Install with: pip install transformers torch")
                self.model = None
                self.tokenizer = None

        # Fallback keyword-based detection
        self._init_keyword_detector()

        logger.info(f"Profanity detector initialized (ML: {bool(self.model)}, Keywords: True)")

    def _init_keyword_detector(self):
        """Initialize comprehensive keyword-based detector"""

        # Expanded profanity word list (severity scores)
        self.profanity_words = {
            # Mild profanity (0.2-0.4)
            'pahus': 0.2,
            'hitto': 0.3,
            'hitsi': 0.3,
            'herranjumala': 0.2,
            'herranjestas': 0.2,
            'helvetti': 0.4,
            'perkele': 0.5,
            'saatana': 0.5,
            'jumalauta': 0.4,

            # Moderate profanity (0.5-0.7)
            'vittu': 0.8,
            'paska': 0.6,
            'paskapuhe': 0.6,
            'persereikä': 0.7,
            'kusipää': 0.7,
            'mulkku': 0.7,
            'idiootti': 0.6,
            'tyhmä': 0.4,
            'ääliö': 0.5,

            # Strong toxic content (0.7-0.9)
            'vihaan': 0.7,
            'tapan': 0.9,
            'kuole': 0.8,
            'kuolema': 0.7,
            'inhoan': 0.7,
            'ruma': 0.5,
            'lihava': 0.5,

            # Slurs and hate speech (0.8-1.0)
            'neekeri': 0.95,
            'homo': 0.7,
            'lesbo': 0.7,
            'huora': 0.85,
        }

        # Toxic phrase patterns
        self.toxic_patterns = [
            r'ole\w*\s+tyhmä',
            r'vihaan\s+sinua',
            r'kuole\w*',
            r'tapan\s+sinut',
            r'ole\w*\s+hiljaa',
            r'sinä\s+idiootti',
        ]

        # Build regex patterns for morphological variants
        self.profanity_patterns = {}
        for word, severity in self.profanity_words.items():
            pattern = rf'\b{word}\w*\b'
            self.profanity_patterns[pattern] = severity

    def _detect_with_ml(self, text: str) -> Optional[float]:
        """
        Detect toxicity using ML model (FinBERT)

        Returns:
            Toxicity score (0-1) or None if model unavailable
        """
        if not self.model or not self.tokenizer:
            return None

        try:
            import torch

            # Tokenize
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

            # Get prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.nn.functional.softmax(logits, dim=-1)

                # Assuming binary classification: [non-toxic, toxic]
                toxicity_score = probabilities[0][1].item()

            return toxicity_score

        except Exception as e:
            logger.warning(f"ML detection failed: {e}")
            return None

    def _detect_with_keywords(self, text: str) -> tuple[float, List[tuple]]:
        """
        Detect toxicity using keyword matching

        Returns:
            (toxicity_score, findings)
            findings: List of (word, position, confidence)
        """
        findings = []
        text_lower = text.lower()

        # Check profanity patterns
        for pattern, severity in self.profanity_patterns.items():
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                findings.append((
                    match.group(),
                    match.start(),
                    severity
                ))

        # Check toxic phrases
        for pattern in self.toxic_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                findings.append((
                    match.group(),
                    match.start(),
                    0.8  # High severity for toxic phrases
                ))

        # Calculate overall toxicity
        if not findings:
            return 0.0, []

        # Average severity weighted by density
        avg_severity = sum(f[2] for f in findings) / len(findings)
        words = re.findall(r'\b[\w]+\b', text)
        density_factor = min(len(findings) / max(len(words), 1) * 10, 1.0)

        toxicity_score = min((avg_severity * 0.7) + (density_factor * 0.3), 1.0)

        return round(toxicity_score, 3), findings

    def _determine_severity(self, toxicity_score: float) -> str:
        """Determine severity level"""
        if toxicity_score >= 0.7:
            return "High"
        elif toxicity_score >= 0.4:
            return "Medium"
        elif toxicity_score >= 0.2:
            return "Low"
        else:
            return "None"

    def detect(
        self,
        text: str,
        return_flagged_words: bool = False,
        threshold: float = 0.5
    ) -> ProfanityResponse:
        """
        Detect profanity and toxicity using ML or keywords

        Args:
            text: Input text to check
            return_flagged_words: Return list of flagged words
            threshold: Detection threshold (0-1)

        Returns:
            ProfanityResponse
        """
        logger.info(f"Checking profanity for text: {text[:50]}... (ML: {bool(self.model)})")

        # Try ML detection first
        ml_score = self._detect_with_ml(text)

        if ml_score is not None:
            # Use ML score
            toxicity_score = ml_score
            flagged_words = None  # ML model doesn't provide word-level attribution easily
            method = "ml"
        else:
            # Fallback to keyword detection
            toxicity_score, findings = self._detect_with_keywords(text)
            method = "keywords"

            # Prepare flagged words if requested
            flagged_words = None
            if return_flagged_words and findings:
                flagged_words = [
                    FlaggedWord(
                        word=word,
                        position=position,
                        confidence=confidence
                    )
                    for word, position, confidence in findings
                ]

        # Determine if toxic based on threshold
        is_toxic = toxicity_score >= threshold

        # Determine severity
        severity = self._determine_severity(toxicity_score)

        result = ProfanityResponse(
            text=text,
            is_toxic=is_toxic,
            toxicity_score=toxicity_score,
            flagged_words=flagged_words,
            severity=severity
        )

        logger.info(f"Profanity check complete: {severity} severity ({toxicity_score} score) using {method}")
        return result
