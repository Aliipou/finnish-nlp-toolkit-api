"""
Unit tests for Profanity Detection Model
"""
import pytest
from app.services.profanity_model import ProfanityDetector


class TestProfanityDetector:
    """Test cases for ProfanityDetector"""

    @pytest.fixture
    def detector(self):
        """Create profanity detector instance for testing"""
        return ProfanityDetector()

    def test_initialization(self, detector):
        """Test detector initializes correctly"""
        assert detector is not None
        assert len(detector.profanity_words) > 0
        assert len(detector.profanity_patterns) > 0

    def test_clean_text(self, detector):
        """Test that clean text is not flagged"""
        result = detector.detect("Tämä on puhdas teksti")
        assert result.is_toxic is False
        assert result.toxicity_score < 0.5
        assert result.severity in ["None", "Low"]

    def test_profane_text(self, detector):
        """Test that profane text is detected"""
        result = detector.detect("vittu")
        assert result.is_toxic is True
        assert result.toxicity_score > 0.5
        assert result.severity in ["Medium", "High"]

    def test_threshold_low(self, detector):
        """Test detection with low threshold"""
        result = detector.detect("hitto", threshold=0.1)
        assert result.is_toxic is True  # Should be detected with low threshold

    def test_threshold_high(self, detector):
        """Test detection with high threshold"""
        result = detector.detect("hitto", threshold=0.9)
        assert result.is_toxic is False  # Might not be detected with high threshold

    def test_flagged_words_returned(self, detector):
        """Test that flagged words are returned when requested"""
        result = detector.detect("vittu paska", return_flagged_words=True)
        assert result.flagged_words is not None
        assert len(result.flagged_words) > 0

    def test_flagged_words_not_returned(self, detector):
        """Test that flagged words are not returned when not requested"""
        result = detector.detect("vittu paska", return_flagged_words=False)
        assert result.flagged_words is None

    def test_flagged_word_structure(self, detector):
        """Test structure of flagged words"""
        result = detector.detect("vittu", return_flagged_words=True)
        if result.flagged_words:
            flagged = result.flagged_words[0]
            assert hasattr(flagged, 'word')
            assert hasattr(flagged, 'position')
            assert hasattr(flagged, 'confidence')
            assert 0 <= flagged.confidence <= 1

    def test_severity_levels(self, detector):
        """Test different severity levels"""
        # Clean text
        clean = detector.detect("Hei, mitä kuuluu?")
        assert clean.severity == "None"

        # Profane text
        profane = detector.detect("vittu")
        assert profane.severity in ["Low", "Medium", "High"]

    def test_multiple_profanity(self, detector):
        """Test text with multiple profane words"""
        result = detector.detect("vittu paska saatana")
        # Should have higher toxicity than single word
        assert result.toxicity_score > 0.5

    def test_morphological_variants(self, detector):
        """Test that morphological variants are detected"""
        # Base form
        base = detector.detect("vittu")
        # Variant with suffix
        variant = detector.detect("vittua")

        # Both should be detected
        assert base.is_toxic is True
        assert variant.is_toxic is True

    def test_empty_text(self, detector):
        """Test handling of empty text"""
        result = detector.detect("")
        assert result.is_toxic is False
        assert result.toxicity_score == 0.0
        assert result.severity == "None"

    def test_mixed_content(self, detector):
        """Test text with both clean and profane content"""
        result = detector.detect("Hei, mitä vittu kuuluu?", return_flagged_words=True)
        assert result.is_toxic is True
        # Should have flagged words but not all words
        if result.flagged_words:
            assert len(result.flagged_words) < 4

    def test_case_insensitivity(self, detector):
        """Test that detection is case insensitive"""
        lower = detector.detect("vittu")
        upper = detector.detect("VITTU")
        mixed = detector.detect("Vittu")

        # All should be detected
        assert lower.is_toxic is True
        assert upper.is_toxic is True
        assert mixed.is_toxic is True

    def test_toxicity_score_range(self, detector):
        """Test that toxicity score is always 0-1"""
        test_texts = [
            "puhdas teksti",
            "vittu",
            "vittu paska saatana helvetti"
        ]

        for text in test_texts:
            result = detector.detect(text)
            assert 0.0 <= result.toxicity_score <= 1.0

    def test_response_structure(self, detector):
        """Test that response has all required fields"""
        result = detector.detect("testi")
        assert hasattr(result, 'text')
        assert hasattr(result, 'is_toxic')
        assert hasattr(result, 'toxicity_score')
        assert hasattr(result, 'severity')
        assert result.text == "testi"
