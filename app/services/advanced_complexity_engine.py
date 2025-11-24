"""
Advanced Finnish Text Complexity Analysis with UDPipe & spaCy
Real dependency parsing for accurate complexity metrics
"""
import re
import logging
from typing import List, Dict, Optional
from app.models.schemas import ComplexityResponse, CaseDistribution

logger = logging.getLogger(__name__)


class AdvancedComplexityEngine:
    """
    Production-grade complexity analyzer using UDPipe or spaCy
    Falls back to heuristics if libraries unavailable
    """

    def __init__(self, use_udpipe: bool = True, use_spacy: bool = True):
        """
        Initialize advanced complexity analyzer

        Args:
            use_udpipe: Try to use UDPipe for parsing
            use_spacy: Try to use spaCy for analysis
        """
        logger.info("Initializing Advanced Complexity Analysis Engine")

        self.udpipe_model = None
        self.spacy_nlp = None
        self.use_udpipe = use_udpipe
        self.use_spacy = use_spacy

        # Try UDPipe
        if use_udpipe:
            try:
                from ufal.udpipe import Model, Pipeline
                # Note: Actual model file would need to be downloaded
                # Model available at: https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3131
                model_path = "data/models/finnish-tdt-ud-2.5-191206.udpipe"
                try:
                    self.udpipe_model = Model.load(model_path)
                    if self.udpipe_model:
                        self.udpipe_pipeline = Pipeline(self.udpipe_model, "tokenize", Pipeline.DEFAULT, Pipeline.DEFAULT, "conllu")
                        logger.info("✅ UDPipe model loaded successfully")
                    else:
                        raise Exception("Model file not found")
                except:
                    logger.warning(f"⚠️  UDPipe model not found at {model_path}")
                    logger.warning("Download from: https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3131")
                    self.udpipe_model = None
            except ImportError:
                logger.warning("⚠️  ufal.udpipe not available")
                logger.warning("Install with: pip install ufal.udpipe")
                self.udpipe_model = None

        # Try spaCy
        if use_spacy:
            try:
                import spacy
                try:
                    self.spacy_nlp = spacy.load("fi_core_news_sm")
                    logger.info("✅ spaCy Finnish model loaded successfully")
                except OSError:
                    logger.warning("⚠️  spaCy Finnish model not found")
                    logger.warning("Install with: python -m spacy download fi_core_news_sm")
                    self.spacy_nlp = None
            except ImportError:
                logger.warning("⚠️  spaCy not available")
                self.spacy_nlp = None

        # Fallback heuristics
        self._init_fallback_heuristics()

        logger.info(f"Complexity analyzer initialized (UDPipe: {bool(self.udpipe_model)}, spaCy: {bool(self.spacy_nlp)})")

    def _init_fallback_heuristics(self):
        """Initialize fallback heuristic patterns"""
        self.clause_markers = [
            'joka', 'mikä', 'että', 'kun', 'jos', 'koska', 'vaikka',
            'kuin', 'kuten', 'jotta', 'kunnes', 'siksi', 'eli'
        ]
        self.sentence_terminators = ['.', '!', '?']

    def _analyze_with_udpipe(self, text: str) -> Optional[Dict]:
        """
        Analyze text using UDPipe for dependency parsing

        Returns:
            Dict with parse tree and metrics
        """
        if not self.udpipe_model:
            return None

        try:
            processed = self.udpipe_pipeline.process(text)
            lines = processed.split('\n')

            clauses = 0
            words = 0
            cases = {}

            for line in lines:
                if line and not line.startswith('#'):
                    parts = line.split('\t')
                    if len(parts) >= 10:
                        words += 1

                        # Count clauses based on dependency relations
                        dep_rel = parts[7]  # Dependency relation
                        if dep_rel in ['acl', 'acl:relcl', 'advcl', 'ccomp', 'xcomp']:
                            clauses += 1

                        # Extract case information from features
                        feats = parts[5]
                        if 'Case=' in feats:
                            case = feats.split('Case=')[1].split('|')[0]
                            cases[case] = cases.get(case, 0) + 1

            return {
                'clauses': max(clauses, 1),
                'words': words,
                'cases': cases,
                'method': 'udpipe'
            }
        except Exception as e:
            logger.warning(f"UDPipe analysis failed: {e}")
            return None

    def _analyze_with_spacy(self, text: str) -> Optional[Dict]:
        """
        Analyze text using spaCy

        Returns:
            Dict with analysis results
        """
        if not self.spacy_nlp:
            return None

        try:
            doc = self.spacy_nlp(text)

            clauses = 0
            words = len([token for token in doc if not token.is_punct])
            cases = {}

            for sent in doc.sents:
                # Count subordinate clauses
                for token in sent:
                    if token.dep_ in ['acl', 'advcl', 'ccomp', 'xcomp', 'relcl']:
                        clauses += 1

                    # Extract morphological case
                    if 'Case' in token.morph:
                        case = str(token.morph.get('Case')[0]) if token.morph.get('Case') else 'Nom'
                        cases[case] = cases.get(case, 0) + 1

            return {
                'clauses': max(clauses, len(list(doc.sents))),
                'words': words,
                'cases': cases,
                'method': 'spacy'
            }
        except Exception as e:
            logger.warning(f"spaCy analysis failed: {e}")
            return None

    def _analyze_with_heuristics(self, text: str) -> Dict:
        """Fallback heuristic analysis"""
        sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
        words = re.findall(r'\b[\w]+\b', text)

        # Count clauses (commas + clause markers)
        clauses = len(sentences)
        text_lower = text.lower()
        for marker in self.clause_markers:
            clauses += text_lower.count(f' {marker} ')
        clauses += text.count(',')

        return {
            'clauses': max(clauses, 1),
            'words': len(words),
            'cases': {},  # Can't reliably detect without parsing
            'method': 'heuristic'
        }

    def _calculate_morphological_depth(self, analysis: Dict, avg_word_length: float) -> float:
        """
        Calculate morphological depth score (0-100)
        """
        score = 0.0

        # Factor 1: Case variety (0-30 points)
        unique_cases = len(analysis.get('cases', {}))
        score += min(unique_cases * 3, 30)

        # Factor 2: Average word length (0-30 points)
        score += min(avg_word_length * 3, 30)

        # Factor 3: Clause density (0-40 points)
        words = analysis.get('words', 1)
        clauses = analysis.get('clauses', 1)
        clause_density = (clauses / max(words, 1)) * 10
        score += min(clause_density * 20, 40)

        return round(min(score, 100), 2)

    def _determine_complexity_rating(self, morph_score: float, clause_count: int, word_count: int) -> str:
        """Determine overall complexity rating"""
        clauses_per_10_words = (clause_count / max(word_count, 1)) * 10

        if morph_score > 70 or clauses_per_10_words > 3:
            return "Complex"
        elif morph_score > 40 or clauses_per_10_words > 1.5:
            return "Moderate"
        else:
            return "Simple"

    def analyze(self, text: str, detailed: bool = True) -> ComplexityResponse:
        """
        Analyze text complexity using best available method

        Priority: UDPipe > spaCy > Heuristics

        Args:
            text: Input Finnish text
            detailed: Include detailed analysis

        Returns:
            ComplexityResponse
        """
        logger.info(f"Analyzing complexity for text: {text[:50]}...")

        # Try analysis methods in order
        analysis = (self._analyze_with_udpipe(text) or
                    self._analyze_with_spacy(text) or
                    self._analyze_with_heuristics(text))

        method = analysis.get('method', 'unknown')
        logger.info(f"Using analysis method: {method}")

        # Calculate metrics
        words = re.findall(r'\b[\w]+\b', text)
        sentences = len([s for s in re.split(r'[.!?]+', text) if s.strip()])
        word_count = analysis['words']
        clause_count = analysis['clauses']
        avg_word_length = round(sum(len(w) for w in words) / max(len(words), 1), 2)

        # Case distribution
        case_distribution = None
        if detailed:
            case_map = {
                'Nom': 'nominative', 'Gen': 'genitive', 'Par': 'partitive',
                'Ine': 'inessive', 'Ela': 'elative', 'Ill': 'illative',
                'Ade': 'adessive', 'Abl': 'ablative', 'All': 'allative',
                'Ess': 'essive', 'Tra': 'translative'
            }

            case_dist = CaseDistribution()
            for case, count in analysis.get('cases', {}).items():
                field_name = case_map.get(case, 'other')
                if hasattr(case_dist, field_name):
                    setattr(case_dist, field_name, count)

            case_distribution = case_dist

        # Morphological depth
        morph_score = self._calculate_morphological_depth(analysis, avg_word_length)

        # Complexity rating
        complexity_rating = self._determine_complexity_rating(morph_score, clause_count, word_count)

        result = ComplexityResponse(
            text=text,
            sentence_count=sentences,
            word_count=word_count,
            clause_count=clause_count,
            morphological_depth_score=morph_score,
            average_word_length=avg_word_length,
            case_distribution=case_distribution,
            complexity_rating=complexity_rating
        )

        logger.info(f"Complexity analysis complete: {complexity_rating} ({morph_score} score) using {method}")
        return result
