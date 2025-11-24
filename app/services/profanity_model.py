"""
Finnish Profanity/Toxicity Detection Model
Detects profanity and toxic content in Finnish text
"""
import re
import logging
from typing import List, Optional
from app.models.schemas import ProfanityResponse, FlaggedWord

logger = logging.getLogger(__name__)


class ProfanityDetector:
    """
    Detects profanity and toxicity in Finnish text
    Uses keyword matching and pattern-based detection
    """

    def __init__(self):
        """Initialize profanity detector"""
        logger.info("Initializing Profanity Detection Model")

        # Finnish profanity words (sample list - in production use comprehensive dataset)
        # Note: These are example words for demonstration
        self.profanity_words = {
            # Mild profanity (score: 0.3-0.5)
            'perkele': 0.5,
            'helvetti': 0.4,
            'saatana': 0.5,
            'jumalauta': 0.4,
            'hitto': 0.3,
            'pahus': 0.2,

            # Strong profanity (score: 0.6-0.8)
            'vittu': 0.8,
            'paska': 0.6,
            'kusipää': 0.7,
            'idiootti': 0.6,
            'tyhmä': 0.4,

            # Toxic patterns (score: 0.7-0.9)
            'vihaan': 0.7,
            'tapan': 0.9,
            'kuole': 0.8,
        }

        # Profanity word variants (with common morphological forms)
        self.profanity_patterns = self._build_profanity_patterns()

        # Toxic phrase patterns
        self.toxic_patterns = [
            r'ole\w*\s+tyhmä',
            r'vihaan\s+sinua',
            r'kuole\w*',
            r'tapan\s+sinut',
        ]

        logger.info(f"Loaded {len(self.profanity_words)} profanity words")
        logger.info("Profanity detector initialized successfully")

    def _build_profanity_patterns(self) -> dict:
        """
        Build regex patterns for profanity words including morphological variants
        """
        patterns = {}

        for word, severity in self.profanity_words.items():
            # Create pattern that matches the word with common endings
            pattern = rf'\b{word}\w*\b'
            patterns[pattern] = severity

        return patterns

    def _find_profanity_words(self, text: str) -> List[tuple]:
        """
        Find profanity words in text
        Returns list of (word, position, confidence)
        """
        findings = []
        text_lower = text.lower()

        # Check each profanity pattern
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

        return findings

    def _calculate_toxicity_score(self, findings: List[tuple], word_count: int) -> float:
        """
        Calculate overall toxicity score based on findings
        """
        if not findings:
            return 0.0

        # Base score from average severity of found words
        avg_severity = sum(f[2] for f in findings) / len(findings)

        # Density factor (more profanity = higher score)
        density_factor = min(len(findings) / max(word_count, 1) * 10, 1.0)

        # Combined score
        toxicity = min((avg_severity * 0.7) + (density_factor * 0.3), 1.0)

        return round(toxicity, 3)

    def _determine_severity(self, toxicity_score: float) -> str:
        """
        Determine severity level based on toxicity score
        """
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
        Detect profanity and toxicity in text

        Args:
            text: Input text to check
            return_flagged_words: Whether to return list of flagged words
            threshold: Detection threshold (0-1)

        Returns:
            ProfanityResponse with toxicity analysis
        """
        logger.info(f"Checking profanity for text: {text[:50]}...")

        # Find profanity
        findings = self._find_profanity_words(text)

        # Calculate word count
        words = re.findall(r'\b[\w]+\b', text)
        word_count = len(words)

        # Calculate toxicity score
        toxicity_score = self._calculate_toxicity_score(findings, word_count)

        # Determine if toxic based on threshold
        is_toxic = toxicity_score >= threshold

        # Determine severity
        severity = self._determine_severity(toxicity_score)

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

        result = ProfanityResponse(
            text=text,
            is_toxic=is_toxic,
            toxicity_score=toxicity_score,
            flagged_words=flagged_words,
            severity=severity
        )

        logger.info(f"Profanity check complete: {severity} severity ({toxicity_score} score)")
        return result
