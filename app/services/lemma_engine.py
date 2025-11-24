"""
Finnish Lemmatizer Engine
Implements rule-based lemmatization with morphological analysis
"""
import re
import logging
from typing import List, Dict, Optional
from app.models.schemas import LemmatizationResponse, WordLemma

logger = logging.getLogger(__name__)


class LemmatizerEngine:
    """
    Finnish text lemmatizer with morphological analysis
    Uses rule-based patterns for Finnish morphology
    """

    def __init__(self):
        """Initialize the lemmatizer with Finnish morphological rules"""
        logger.info("Initializing Finnish Lemmatizer Engine")

        # Finnish case suffixes - order matters! (longer patterns first, plural before singular)
        self.case_patterns = [
            # Plural forms (check these first, longest suffixes first!)
            ('partitive', 'plural', ['oja', 'öjä', 'ita', 'itä', 'ia', 'iä']),
            ('genitive', 'plural', ['iden', 'itten', 'ojen', 'öjen', 'jen', 'ien', 'en']),
            ('inessive', 'plural', ['issa', 'issä']),
            ('elative', 'plural', ['ista', 'istä']),
            ('illative', 'plural', ['isiin', 'ihin', 'oihin', 'öihin']),
            ('adessive', 'plural', ['oilla', 'öillä', 'illa', 'illä']),
            ('ablative', 'plural', ['oilta', 'öiltä', 'ilta', 'iltä']),
            ('allative', 'plural', ['oille', 'öille', 'ille']),
            ('essive', 'plural', ['oina', 'öinä', 'ina', 'inä']),
            ('translative', 'plural', ['oiksi', 'öiksi', 'iksi']),

            # Singular forms (longest suffixes first!)
            ('illative', 'singular', ['seen', 'siin', 'hin', 'hon', 'hön', 'hun', 'hyn']),
            ('inessive', 'singular', ['ssa', 'ssä']),
            ('elative', 'singular', ['sta', 'stä']),
            ('adessive', 'singular', ['lla', 'llä']),
            ('ablative', 'singular', ['lta', 'ltä']),
            ('allative', 'singular', ['lle']),
            ('translative', 'singular', ['ksi']),
            ('essive', 'singular', ['na', 'nä']),
            ('partitive', 'singular', ['aa', 'ää', 'ta', 'tä', 'a', 'ä']),
            # Genitive last for singular (just 'n'), most ambiguous
            ('genitive', 'singular', ['n']),
        ]

        # Nominative plural markers
        self.nominative_plural_suffixes = ['t']

        # Common verb endings
        self.verb_endings = {
            'present': ['n', 't', 'mme', 'tte', 'vat', 'vät'],
            'past': ['in', 'it', 'imme', 'itte', 'ivat', 'ivät'],
            'conditional': ['isin', 'isit', 'isi', 'isimme', 'isitte', 'isivat', 'isivät'],
        }

        # Common Finnish words dictionary (lemma -> forms)
        self.known_words = self._load_known_words()

        logger.info("Lemmatizer initialized successfully")

    def _load_known_words(self) -> Dict[str, List[str]]:
        """
        Load common Finnish words and their forms
        Includes different inflection types (sanatyypit) and irregular forms
        In production, this would load from a comprehensive database
        """
        return {
            # Irregular and exception words
            'ihminen': [
                # Type 38: -nen words (ihminen -> ihmise-)
                'ihminen', 'ihmisen', 'ihmistä', 'ihmisessä', 'ihmisestä', 'ihmiseen',
                'ihmisellä', 'ihmiseltä', 'ihmiselle', 'ihmisenä', 'ihmiseksi',
                'ihmiset', 'ihmisten', 'ihmisiä', 'ihmisissä', 'ihmisistä', 'ihmisiin',
                'ihmisillä', 'ihmisiltä', 'ihmisille', 'ihmisinä', 'ihmisiksi'
            ],
            'nainen': [
                # Type 38: -nen words (nainen -> naise-)
                'nainen', 'naisen', 'naista', 'naisessa', 'naisesta', 'naiseen',
                'naisella', 'naiselta', 'naiselle', 'naisena', 'naiseksi',
                'naiset', 'naisten', 'naisia', 'naisissa', 'naisista', 'naisiin',
                'naisilla', 'naisilta', 'naisille', 'naisina', 'naisiksi'
            ],
            'paras': [
                # Irregular adjective (paras -> paraa-)
                'paras', 'parhaan', 'parasta', 'parhaassa', 'parhaasta', 'parhaaseen',
                'parhaalla', 'parhaalta', 'parhaalle', 'parhaana', 'parhaaksi',
                'parhaat', 'parhaiden', 'parhaita', 'parhaissa', 'parhaista',
                'parhaisiin', 'parhailla', 'parhailta', 'parhaille', 'parhaina', 'parhaiksi'
            ],
            'hyvä': [
                # Type 10: -vä/-pä words with gradation
                'hyvä', 'hyvän', 'hyvää', 'hyvässä', 'hyvästä', 'hyvään',
                'hyvällä', 'hyvältä', 'hyvälle', 'hyvänä', 'hyväksi',
                'hyvät', 'hyvien', 'hyviä', 'hyvissä', 'hyvistä', 'hyviin',
                'hyvillä', 'hyviltä', 'hyville', 'hyvinä', 'hyviksi'
            ],
            # Nouns with both singular and plural forms
            'kissa': [
                # Singular
                'kissa', 'kissan', 'kissaa', 'kissassa', 'kissasta', 'kissaan',
                'kissalla', 'kissalta', 'kissalle', 'kissana', 'kissaksi',
                # Plural
                'kissat', 'kissojen', 'kissoja', 'kissoissa', 'kissoista',
                'kissoihin', 'kissoilla', 'kissoilta', 'kissoille', 'kissoina', 'kissoiksi'
            ],
            'koira': [
                # Singular
                'koira', 'koiran', 'koiraa', 'koirassa', 'koirasta', 'koiraan',
                'koiralla', 'koiralta', 'koiralle', 'koirana', 'koiraksi',
                # Plural
                'koirat', 'koirien', 'koiria', 'koirissa', 'koirista',
                'koiriin', 'koirilla', 'koirilta', 'koirille', 'koirina', 'koiriksi'
            ],
            'talo': [
                # Singular
                'talo', 'talon', 'taloa', 'talossa', 'talosta', 'taloon',
                'talolla', 'talolta', 'talolle', 'talona', 'taloksi',
                # Plural
                'talot', 'talojen', 'taloja', 'taloissa', 'taloista',
                'taloihin', 'taloilla', 'taloilta', 'taloille', 'taloina', 'taloiksi'
            ],
            'auto': [
                # Singular
                'auto', 'auton', 'autoa', 'autossa', 'autosta', 'autoon',
                'autolla', 'autolta', 'autolle', 'autona', 'autoksi',
                # Plural
                'autot', 'autojen', 'autoja', 'autoissa', 'autoista',
                'autoihin', 'autoilla', 'autoilta', 'autoille', 'autoina', 'autoiksi'
            ],
            'hiiri': [
                # Singular
                'hiiri', 'hiiren', 'hiirtä', 'hiiressä', 'hiirestä', 'hiireen',
                'hiirellä', 'hiireltä', 'hiirelle', 'hiirenä', 'hiireksi',
                # Plural
                'hiiret', 'hiirten', 'hiiriä', 'hiirissä', 'hiiristä',
                'hiiriin', 'hiirillä', 'hiiriltä', 'hiirille', 'hiirinä', 'hiiriksi'
            ],
            'puutarha': ['puutarha', 'puutarhan', 'puutarhaa', 'puutarhassa', 'puutarhasta', 'puutarhaan'],

            # Verbs
            'syödä': ['syö', 'söi', 'syö', 'söivät', 'syödä'],
            'juosta': ['juokse', 'juoksi', 'juoksee', 'juoksivat', 'juosta'],
            'olla': ['on', 'oli', 'ovat', 'olivat', 'olla'],

            # Adjectives
            'nopea': ['nopea', 'nopean', 'nopeaa', 'nopeasti'],
            'iso': ['iso', 'ison', 'isoa', 'isossa'],
            'pieni': ['pieni', 'pienen', 'pientä'],
        }

    def _identify_pos(self, word: str) -> str:
        """
        Identify part of speech
        Simple heuristic-based approach
        """
        # Check if it ends with typical adverb suffix
        if word.endswith('sti'):
            return 'ADV'

        # Check for verb infinitive
        if word.endswith(('da', 'dä', 'ta', 'tä', 'la', 'lä', 'ra', 'rä', 'na', 'nä')):
            return 'VERB'

        # Default to noun
        return 'NOUN'

    def _extract_morphology(self, original: str, lemma: str) -> Dict[str, str]:
        """
        Extract morphological features from the word
        Returns case and number (singular/plural)
        Special handling for -nen words (Type 38)
        """
        features = {
            'case': 'Nominative',
            'number': 'Singular'
        }

        original_lower = original.lower()

        # If word hasn't changed, it's nominative singular
        if original_lower == lemma:
            return features

        # Special handling for -nen words (Type 38)
        # nainen uses different stems for different cases:
        # - Most cases: naise- (naisen, naisessa, naiset)
        # - Partitive singular: nais- (naista, NOT naiseta!)
        if lemma.endswith('nen'):
            base = lemma[:-3]  # remove 'nen' -> 'nai' from 'nainen'
            stem_se = base + 'se'  # 'naise' for most inflections
            stem_s = base + 's'    # 'nais' for partitive singular

            # Partitive singular: naista = nais + ta (special stem!)
            if original_lower == stem_s + 'ta' or original_lower == stem_s + 'tä':
                features['case'] = 'Partitive'
                features['number'] = 'Singular'
                return features

            # Check if original uses the regular 'naise' stem
            if stem_se in original_lower:
                # Genitive singular: naisen = naise + n
                if original_lower == stem_se + 'n':
                    features['case'] = 'Genitive'
                    features['number'] = 'Singular'
                    return features

                # Nominative plural: naiset = naise + t
                if original_lower == stem_se + 't':
                    features['case'] = 'Nominative'
                    features['number'] = 'Plural'
                    return features

                # For other cases, match patterns using naise- stem
                for case, number, suffixes in self.case_patterns:
                    for suffix in suffixes:
                        if original_lower == stem_se + suffix:
                            features['case'] = case.capitalize()
                            features['number'] = number.capitalize()
                            return features

        # Check for nominative plural (ends with -t)
        if original_lower.endswith('t') and len(original_lower) > 2:
            # Check if removing 't' gives us the lemma
            if original_lower[:-1] == lemma:
                features['case'] = 'Nominative'
                features['number'] = 'Plural'
                return features

        # Check all case patterns (plural patterns are checked first!)
        for case, number, suffixes in self.case_patterns:
            for suffix in suffixes:
                if original_lower.endswith(suffix):
                    # Make sure the suffix is significant (word is long enough)
                    if len(original_lower) > len(suffix) + 1:
                        features['case'] = case.capitalize()
                        features['number'] = number.capitalize()
                        return features

        return features

    def _lemmatize_word(self, word: str, include_morphology: bool = True) -> WordLemma:
        """
        Lemmatize a single word
        """
        # Clean the word
        original_word = word
        word_lower = word.lower()

        # Check if word is in known words dictionary
        for lemma, forms in self.known_words.items():
            if word_lower in forms:
                morphology = self._extract_morphology(word_lower, lemma) if include_morphology else None
                pos = self._identify_pos(lemma)
                return WordLemma(
                    original=original_word,
                    lemma=lemma,
                    pos=pos,
                    morphology=morphology
                )

        # Rule-based lemmatization
        lemma = self._rule_based_lemmatize(word_lower)
        morphology = self._extract_morphology(word_lower, lemma) if include_morphology else None
        pos = self._identify_pos(word_lower)

        return WordLemma(
            original=original_word,
            lemma=lemma,
            pos=pos,
            morphology=morphology
        )

    def _rule_based_lemmatize(self, word: str) -> str:
        """
        Apply rule-based lemmatization for unknown words
        Handles Finnish morphology: plural forms, vowel harmony, stem changes
        Special handling for common word types (sanatyypit):
        - Type 38: -nen words (nainen -> naise- -> nainen)
        - Consonant gradation patterns
        - Vowel harmony
        """
        lemma = word.lower()

        # Special handling for -nen words (Type 38)
        # These change stems: nainen -> naise- (most cases) or nais- (partitive sg)
        # Examples: naisessa (naise+ssa), naista (nais+ta)

        # Check for partitive singular pattern: ends with 'sta' or 'stä'
        if (lemma.endswith('sta') or lemma.endswith('stä')) and len(lemma) > 4:
            # naista -> nais+ta -> nai+nen = nainen
            stem = lemma[:-2]  # remove 'ta' or 'tä'
            if stem.endswith('s'):
                base = stem[:-1]  # remove 's'
                return base + 'nen'

        # Check for other -nen word patterns (with 'ise' or 'se' stem)
        if ('ise' in lemma or lemma.endswith('se')) and len(lemma) > 5:
            # Try to reconstruct the -nen form
            # naisessa -> remove suffix -> naise -> remove 'se' -> nai -> add 'nen' -> nainen
            for case, number, suffixes in self.case_patterns:
                for suffix in suffixes:
                    if lemma.endswith(suffix):
                        stem = lemma[:-len(suffix)]
                        # Check if stem ends with 'ise' or just 'se'
                        if stem.endswith('ise'):
                            # Remove 'ise' and add 'inen'
                            base = stem[:-3]
                            return base + 'nen'
                        elif stem.endswith('se'):
                            # Remove 'se' and add 'nen'
                            base = stem[:-2]
                            return base + 'nen'

        # First, check for nominative plural (ends with -t)
        if lemma.endswith('t') and len(lemma) > 3:
            # Remove the -t
            lemma = lemma[:-1]
            # Handle double vowels (talot -> talo, not talot -> talo)
            if lemma.endswith(('aa', 'ää', 'ee', 'ii', 'oo', 'öö', 'uu', 'yy')):
                lemma = lemma[:-1]
            return lemma

        # Try to match and remove case endings (check plural forms first!)
        for case, number, suffixes in self.case_patterns:
            for suffix in suffixes:
                if lemma.endswith(suffix) and len(lemma) > len(suffix) + 2:
                    # Remove the suffix
                    stem = lemma[:-len(suffix)]

                    # Handle plural stem with 'i' or 'j' marker
                    if number == 'plural':
                        # Remove plural 'i' if present before removed suffix
                        if stem.endswith('i') and len(stem) > 2:
                            # Only remove if preceded by consonant (kissoi -> kisso -> kissa)
                            if stem[-2] not in 'aeiouyäö':
                                stem = stem[:-1]

                        # Remove 'j' plural marker (kissoj -> kisso)
                        if stem.endswith('j') and len(stem) > 2:
                            stem = stem[:-1]

                        # Remove 'o'/'ö' if it was added for plural stem (kisso -> kissa)
                        if len(stem) > 2 and stem.endswith('o') and stem[-2] not in 'o':
                            # Check vowel harmony
                            has_back = any(v in stem for v in 'aou')
                            has_front = any(v in stem for v in 'äöy')
                            if has_front and not has_back:
                                # Should be 'ö', try replacing o with nothing or original
                                stem = stem[:-1] + 'a'
                            elif has_back:
                                stem = stem[:-1] + 'a'
                        elif len(stem) > 2 and stem.endswith('ö') and stem[-2] not in 'ö':
                            stem = stem[:-1] + 'ä'

                    # Handle double vowels that appear due to stem changes
                    if stem.endswith(('aa', 'ää', 'ee', 'ii', 'oo', 'öö', 'uu', 'yy')):
                        stem = stem[:-1]

                    # Handle single partitive vowel addition (talo+a -> talo)
                    # Already handled by not having the vowel

                    return stem

        # If no pattern matched, return as is
        return lemma

    def _tokenize(self, text: str) -> List[str]:
        """
        Simple tokenization for Finnish text
        """
        # Split on whitespace and punctuation, but keep words
        tokens = re.findall(r'\b[\w]+\b', text)
        return tokens

    def lemmatize(self, text: str, include_morphology: bool = True) -> LemmatizationResponse:
        """
        Lemmatize Finnish text

        Args:
            text: Input Finnish text
            include_morphology: Whether to include morphological analysis

        Returns:
            LemmatizationResponse with lemmatized words
        """
        logger.info(f"Lemmatizing text: {text[:50]}...")

        # Tokenize
        tokens = self._tokenize(text)

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
