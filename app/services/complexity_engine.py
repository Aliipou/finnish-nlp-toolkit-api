"""
Finnish Text Complexity Analysis Engine
Analyzes sentence complexity, morphological depth, and grammatical features
"""
import re
import logging
from typing import List, Dict
from app.models.schemas import ComplexityResponse, CaseDistribution

logger = logging.getLogger(__name__)


class ComplexityEngine:
    """
    Analyzes complexity of Finnish text
    """

    def __init__(self):
        """Initialize complexity analyzer"""
        logger.info("Initializing Complexity Analysis Engine")

        # Clause markers
        self.clause_markers = [
            'joka', 'mikä', 'että', 'kun', 'jos', 'koska', 'vaikka',
            'kuin', 'kuten', 'jotta', 'kunnes', 'siksi', 'eli'
        ]

        # Sentence terminators
        self.sentence_terminators = ['.', '!', '?']

        # Case markers for detection
        self.case_patterns = {
            'nominative': r'\b\w+\b(?![a-zäö])',  # Base form
            'genitive': r'\b\w+n\b',
            'partitive': r'\b\w+(a|ä|ta|tä)\b',
            'inessive': r'\b\w+(ssa|ssä)\b',
            'elative': r'\b\w+(sta|stä)\b',
            'illative': r'\b\w+(an|än|seen|hin|hon|hön)\b',
            'adessive': r'\b\w+(lla|llä)\b',
            'ablative': r'\b\w+(lta|ltä)\b',
            'allative': r'\b\w+lle\b',
            'essive': r'\b\w+(na|nä)\b',
            'translative': r'\b\w+ksi\b',
        }

        # Morphological complexity indicators
        self.complexity_indicators = {
            'long_words': 10,  # Words longer than this are complex
            'case_variety': 5,  # Using 5+ different cases indicates complexity
            'clause_threshold': 2,  # More than 2 clauses = complex
        }

        logger.info("Complexity analyzer initialized successfully")

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences
        """
        sentences = []
        current_sentence = ""

        for char in text:
            current_sentence += char
            if char in self.sentence_terminators:
                sentences.append(current_sentence.strip())
                current_sentence = ""

        if current_sentence.strip():
            sentences.append(current_sentence.strip())

        return [s for s in sentences if s]

    def _count_clauses(self, text: str) -> int:
        """
        Count number of clauses in text
        Clauses are separated by clause markers or commas
        """
        # Base clause count (at least 1 per sentence)
        sentences = self._split_sentences(text)
        clause_count = len(sentences)

        # Add clauses based on markers
        text_lower = text.lower()
        for marker in self.clause_markers:
            clause_count += text_lower.count(f' {marker} ')
            clause_count += text_lower.count(f',{marker} ')

        # Count commas as potential clause separators
        clause_count += text.count(',')

        return max(clause_count, 1)

    def _analyze_case_distribution(self, text: str) -> CaseDistribution:
        """
        Analyze distribution of grammatical cases in text
        """
        text_lower = text.lower()
        distribution = CaseDistribution()

        # Count each case
        for case, pattern in self.case_patterns.items():
            matches = re.findall(pattern, text_lower)
            count = len(matches)

            # Set the count for each case
            if case == 'nominative':
                distribution.nominative = count
            elif case == 'genitive':
                distribution.genitive = count
            elif case == 'partitive':
                distribution.partitive = count
            elif case == 'inessive':
                distribution.inessive = count
            elif case == 'elative':
                distribution.elative = count
            elif case == 'illative':
                distribution.illative = count
            elif case == 'adessive':
                distribution.adessive = count
            elif case == 'ablative':
                distribution.ablative = count
            elif case == 'allative':
                distribution.allative = count
            elif case == 'essive':
                distribution.essive = count
            elif case == 'translative':
                distribution.translative = count

        return distribution

    def _calculate_morphological_depth(self, text: str, case_dist: CaseDistribution) -> float:
        """
        Calculate morphological depth score (0-100)
        Higher score = more complex morphology
        """
        score = 0.0

        # Factor 1: Case variety (max 30 points)
        cases_used = sum([
            1 for count in [
                case_dist.genitive, case_dist.partitive, case_dist.inessive,
                case_dist.elative, case_dist.illative, case_dist.adessive,
                case_dist.ablative, case_dist.allative, case_dist.essive,
                case_dist.translative
            ] if count > 0
        ])
        score += min(cases_used * 3, 30)

        # Factor 2: Average word length (max 30 points)
        words = re.findall(r'\b[\w]+\b', text)
        if words:
            avg_length = sum(len(w) for w in words) / len(words)
            score += min(avg_length * 3, 30)

        # Factor 3: Clause density (max 40 points)
        sentences = self._split_sentences(text)
        if sentences:
            clauses = self._count_clauses(text)
            clause_density = clauses / len(sentences)
            score += min(clause_density * 20, 40)

        return round(min(score, 100), 2)

    def _determine_complexity_rating(self, morph_score: float, clause_count: int, word_count: int) -> str:
        """
        Determine overall complexity rating
        """
        # Calculate factors
        clauses_per_10_words = (clause_count / max(word_count, 1)) * 10

        if morph_score > 70 or clauses_per_10_words > 3:
            return "Complex"
        elif morph_score > 40 or clauses_per_10_words > 1.5:
            return "Moderate"
        else:
            return "Simple"

    def analyze(self, text: str, detailed: bool = True) -> ComplexityResponse:
        """
        Analyze text complexity

        Args:
            text: Input Finnish text
            detailed: Include detailed analysis

        Returns:
            ComplexityResponse with complexity metrics
        """
        logger.info(f"Analyzing complexity for text: {text[:50]}...")

        # Basic metrics
        sentences = self._split_sentences(text)
        words = re.findall(r'\b[\w]+\b', text)
        sentence_count = len(sentences)
        word_count = len(words)

        # Clause analysis
        clause_count = self._count_clauses(text)

        # Case distribution (if detailed)
        case_distribution = None
        if detailed:
            case_distribution = self._analyze_case_distribution(text)

        # Morphological depth
        if detailed and case_distribution:
            morph_score = self._calculate_morphological_depth(text, case_distribution)
        else:
            morph_score = self._calculate_morphological_depth(text, CaseDistribution())

        # Average word length
        avg_word_length = round(sum(len(w) for w in words) / max(len(words), 1), 2) if words else 0

        # Complexity rating
        complexity_rating = self._determine_complexity_rating(morph_score, clause_count, word_count)

        result = ComplexityResponse(
            text=text,
            sentence_count=sentence_count,
            word_count=word_count,
            clause_count=clause_count,
            morphological_depth_score=morph_score,
            average_word_length=avg_word_length,
            case_distribution=case_distribution if detailed else None,
            complexity_rating=complexity_rating
        )

        logger.info(f"Complexity analysis complete: {complexity_rating} ({morph_score} score)")
        return result
