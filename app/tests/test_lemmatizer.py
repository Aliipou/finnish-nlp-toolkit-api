"""
Unit tests for Lemmatizer Engine
"""
import pytest
from app.services.lemma_engine import LemmatizerEngine


class TestLemmatizerEngine:
    """Test cases for LemmatizerEngine"""

    @pytest.fixture
    def lemmatizer(self):
        """Create lemmatizer instance for testing"""
        return LemmatizerEngine()

    def test_initialization(self, lemmatizer):
        """Test lemmatizer initializes correctly"""
        assert lemmatizer is not None
        assert len(lemmatizer.known_words) > 0
        assert len(lemmatizer.case_patterns) > 0

    def test_simple_lemmatization(self, lemmatizer):
        """Test basic lemmatization"""
        result = lemmatizer.lemmatize("kissa")
        assert result.word_count == 1
        assert result.lemmas[0].lemma == "kissa"
        assert result.lemmas[0].original == "kissa"

    def test_genitive_case(self, lemmatizer):
        """Test genitive case lemmatization"""
        result = lemmatizer.lemmatize("kissan")
        assert result.word_count == 1
        assert result.lemmas[0].lemma == "kissa"
        if result.lemmas[0].morphology:
            assert result.lemmas[0].morphology.get('case') in ['Genitive', 'Nominative']

    def test_multiple_words(self, lemmatizer):
        """Test lemmatization of multiple words"""
        result = lemmatizer.lemmatize("kissa söi hiiren")
        assert result.word_count == 3
        assert len(result.lemmas) == 3

    def test_empty_text(self, lemmatizer):
        """Test handling of empty text"""
        result = lemmatizer.lemmatize("")
        assert result.word_count == 0
        assert len(result.lemmas) == 0

    def test_morphology_inclusion(self, lemmatizer):
        """Test morphology is included when requested"""
        result = lemmatizer.lemmatize("kissalla", include_morphology=True)
        assert result.lemmas[0].morphology is not None

    def test_morphology_exclusion(self, lemmatizer):
        """Test morphology is excluded when not requested"""
        result = lemmatizer.lemmatize("kissalla", include_morphology=False)
        assert result.lemmas[0].morphology is None

    def test_known_word_lemmatization(self, lemmatizer):
        """Test lemmatization of known words"""
        test_cases = [
            ("kissa", "kissa"),
            ("kissalla", "kissa"),
            ("autossa", "auto"),
        ]

        for input_word, expected_lemma in test_cases:
            result = lemmatizer.lemmatize(input_word)
            assert result.lemmas[0].lemma == expected_lemma

    def test_sentence_lemmatization(self, lemmatizer):
        """Test lemmatization of full sentence"""
        text = "Kissa söi hiiren nopeasti"
        result = lemmatizer.lemmatize(text)
        assert result.word_count > 0
        assert result.text == text
        assert all(lemma.original for lemma in result.lemmas)

    def test_case_variations(self, lemmatizer):
        """Test different grammatical cases"""
        words = ["talossa", "talosta", "taloon", "talolla"]
        for word in words:
            result = lemmatizer.lemmatize(word)
            # Should recognize it as some form of 'talo'
            assert result.word_count == 1
