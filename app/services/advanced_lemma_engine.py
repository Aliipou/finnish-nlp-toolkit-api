"""
Advanced Finnish Lemmatizer Engine with Voikko Integration
Real morphological analysis for Finnish language
"""
import logging
from typing import List, Dict, Optional
from app.models.schemas import LemmatizationResponse, WordLemma

logger = logging.getLogger(__name__)


class AdvancedLemmatizerEngine:
    """
    Production-grade Finnish lemmatizer using Voikko library
    Fallback to rule-based for unavailable words
    """

    def __init__(self, use_voikko: bool = True):
        """
        Initialize advanced lemmatizer

        Args:
            use_voikko: Try to use libvoikko if available, fallback to rules
        """
        logger.info("Initializing Advanced Finnish Lemmatizer Engine")

        self.voikko = None
        self.use_voikko = use_voikko

        # Try to import and initialize Voikko
        if use_voikko:
            try:
                import libvoikko
                self.voikko = libvoikko.Voikko("fi")
                logger.info("✅ Voikko library loaded successfully")
            except ImportError:
                logger.warning("⚠️  libvoikko not available, falling back to rule-based lemmatization")
                logger.warning("Install with: pip install libvoikko-python (requires system libvoikko)")
                self.voikko = None
            except Exception as e:
                logger.warning(f"⚠️  Voikko initialization failed: {e}")
                logger.warning("Falling back to rule-based lemmatization")
                self.voikko = None

        # Fallback rule-based patterns
        self._init_fallback_rules()

        logger.info(f"Lemmatizer initialized (Voikko: {'enabled' if self.voikko else 'disabled'})")

    def _init_fallback_rules(self):
        """Initialize fallback rule-based patterns"""
        self.case_suffixes = {
            'genitive': ['n'],
            'partitive': ['a', 'ä', 'ta', 'tä'],
            'inessive': ['ssa', 'ssä'],
            'elative': ['sta', 'stä'],
            'illative': ['an', 'än', 'seen', 'hin', 'hon', 'hön'],
            'adessive': ['lla', 'llä'],
            'ablative': ['lta', 'ltä'],
            'allative': ['lle'],
            'essive': ['na', 'nä'],
            'translative': ['ksi'],
        }

        self.known_words = {
            'kissa': ['kissa', 'kissan', 'kissaa', 'kissassa', 'kissasta'],
            'koira': ['koira', 'koiran', 'koiraa', 'koirassa'],
            'talo': ['talo', 'talon', 'taloa', 'talossa', 'talosta', 'taloon'],
            'auto': ['auto', 'auton', 'autoa', 'autossa'],
            'hiiri': ['hiiri', 'hiiren', 'hiirtä', 'hiiressä'],
            'syödä': ['syö', 'söi', 'syö', 'söivät', 'syödä'],
            'juosta': ['juokse', 'juoksi', 'juoksee', 'juoksivat'],
        }

    def _voikko_analyze(self, word: str) -> Optional[Dict]:
        """
        Analyze word using Voikko

        Returns:
            Dict with lemma and morphological analysis or None
        """
        if not self.voikko:
            return None

        try:
            analyses = self.voikko.analyze(word)
            if not analyses:
                return None

            # Take the first (most likely) analysis
            analysis = analyses[0]

            return {
                'lemma': analysis.get('BASEFORM', word),
                'pos': analysis.get('CLASS', 'UNKNOWN'),
                'number': analysis.get('NUMBER', 'UNKNOWN'),
                'case': analysis.get('SIJAMUOTO', 'UNKNOWN'),
                'mood': analysis.get('MOOD', None),
                'tense': analysis.get('TENSE', None),
                'person': analysis.get('PERSON', None),
            }
        except Exception as e:
            logger.warning(f"Voikko analysis failed for '{word}': {e}")
            return None

    def _rule_based_analyze(self, word: str) -> Dict:
        """Fallback rule-based analysis"""
        word_lower = word.lower()

        # Check known words
        for lemma, forms in self.known_words.items():
            if word_lower in forms:
                return {
                    'lemma': lemma,
                    'pos': 'VERB' if lemma.endswith(('da', 'dä', 'ta', 'tä')) else 'NOUN',
                    'case': 'Nominative',
                    'number': 'Singular'
                }

        # Rule-based lemmatization
        lemma = word_lower
        for case, suffixes in self.case_suffixes.items():
            for suffix in sorted(suffixes, key=len, reverse=True):
                if lemma.endswith(suffix) and len(lemma) > len(suffix) + 2:
                    lemma = lemma[:-len(suffix)]
                    break

        return {
            'lemma': lemma,
            'pos': 'NOUN',
            'case': 'Unknown',
            'number': 'Singular'
        }

    def _lemmatize_word(self, word: str, include_morphology: bool) -> WordLemma:
        """
        Lemmatize single word with Voikko or fallback

        Args:
            word: Word to lemmatize
            include_morphology: Include morphological features

        Returns:
            WordLemma object
        """
        # Try Voikko first
        voikko_result = self._voikko_analyze(word)

        if voikko_result:
            # Use Voikko analysis
            morphology = None
            if include_morphology:
                morphology = {
                    'case': voikko_result.get('case', 'UNKNOWN'),
                    'number': voikko_result.get('number', 'UNKNOWN'),
                }
                if voikko_result.get('mood'):
                    morphology['mood'] = voikko_result['mood']
                if voikko_result.get('tense'):
                    morphology['tense'] = voikko_result['tense']
                if voikko_result.get('person'):
                    morphology['person'] = voikko_result['person']

            return WordLemma(
                original=word,
                lemma=voikko_result['lemma'],
                pos=voikko_result.get('pos', 'UNKNOWN'),
                morphology=morphology
            )
        else:
            # Fallback to rule-based
            analysis = self._rule_based_analyze(word)

            morphology = None
            if include_morphology:
                morphology = {
                    'case': analysis['case'],
                    'number': analysis['number']
                }

            return WordLemma(
                original=word,
                lemma=analysis['lemma'],
                pos=analysis['pos'],
                morphology=morphology
            )

    def lemmatize(self, text: str, include_morphology: bool = True) -> LemmatizationResponse:
        """
        Lemmatize Finnish text using Voikko or fallback

        Args:
            text: Input Finnish text
            include_morphology: Include morphological analysis

        Returns:
            LemmatizationResponse
        """
        logger.info(f"Lemmatizing text: {text[:50]}... (Voikko: {bool(self.voikko)})")

        # Tokenize (simple word extraction)
        import re
        tokens = re.findall(r'\b[\w]+\b', text)

        # Lemmatize each word
        lemmas = []
        for token in tokens:
            if token.strip():
                word_lemma = self._lemmatize_word(token, include_morphology)
                lemmas.append(word_lemma)

        result = LemmatizationResponse(
            text=text,
            lemmas=lemmas,
            word_count=len(lemmas)
        )

        logger.info(f"Lemmatization complete: {len(lemmas)} words processed")
        return result

    def __del__(self):
        """Cleanup Voikko instance"""
        if self.voikko:
            try:
                self.voikko.terminate()
            except:
                pass
