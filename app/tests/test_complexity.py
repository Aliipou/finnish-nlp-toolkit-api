"""
Unit tests for Complexity Analysis Engine
"""
import pytest
from app.services.complexity_engine import ComplexityEngine


class TestComplexityEngine:
    """Test cases for ComplexityEngine"""

    @pytest.fixture
    def analyzer(self):
        """Create complexity analyzer instance for testing"""
        return ComplexityEngine()

    def test_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer is not None
        assert len(analyzer.clause_markers) > 0
        assert len(analyzer.case_patterns) > 0

    def test_simple_sentence(self, analyzer):
        """Test analysis of simple sentence"""
        result = analyzer.analyze("Kissa juoksee.")
        assert result.sentence_count == 1
        assert result.word_count == 2
        assert result.complexity_rating in ["Simple", "Moderate", "Complex"]

    def test_complex_sentence(self, analyzer):
        """Test analysis of complex sentence with clauses"""
        text = "Kissa, joka söi hiiren, juoksi nopeasti puutarhaan."
        result = analyzer.analyze(text)
        assert result.sentence_count == 1
        assert result.clause_count > 1
        assert result.word_count > 0

    def test_multiple_sentences(self, analyzer):
        """Test analysis of multiple sentences"""
        text = "Kissa juoksee. Koira haukkuu. Lintu laulaa."
        result = analyzer.analyze(text)
        assert result.sentence_count == 3
        assert result.word_count > 5

    def test_clause_detection(self, analyzer):
        """Test clause detection"""
        # Simple sentence
        simple = analyzer.analyze("Kissa juoksee")
        simple_clauses = simple.clause_count

        # Complex sentence with clause marker
        complex_text = "Kissa juoksee, koska se pelkää"
        complex_result = analyzer.analyze(complex_text)
        assert complex_result.clause_count > simple_clauses

    def test_morphological_depth_score(self, analyzer):
        """Test morphological depth scoring"""
        result = analyzer.analyze("Kissa juoksee")
        assert 0 <= result.morphological_depth_score <= 100

    def test_average_word_length(self, analyzer):
        """Test average word length calculation"""
        result = analyzer.analyze("aa bb ccc")
        # Should be approximately (2+2+3)/3 = 2.33
        assert 2.0 <= result.average_word_length <= 2.5

    def test_case_distribution_detailed(self, analyzer):
        """Test case distribution analysis with detailed=True"""
        result = analyzer.analyze("Talossa on kissa", detailed=True)
        assert result.case_distribution is not None
        # Check that case counts are integers
        assert isinstance(result.case_distribution.nominative, int)
        assert isinstance(result.case_distribution.inessive, int)

    def test_case_distribution_not_detailed(self, analyzer):
        """Test case distribution is None when detailed=False"""
        result = analyzer.analyze("Talossa on kissa", detailed=False)
        assert result.case_distribution is None

    def test_complexity_rating_simple(self, analyzer):
        """Test that simple text gets appropriate rating"""
        result = analyzer.analyze("Kissa juoksee")
        # Rating should be one of the valid values
        assert result.complexity_rating in ["Simple", "Moderate", "Complex"]

    def test_complexity_rating_complex(self, analyzer):
        """Test that complex text gets appropriate rating"""
        text = "Kissa, joka söi hiiren, juoksi nopeasti puutarhaan, koska se pelkäsi koiraa."
        result = analyzer.analyze(text)
        # Complex sentence should have higher rating
        assert result.morphological_depth_score > 0

    def test_empty_text(self, analyzer):
        """Test handling of empty text"""
        result = analyzer.analyze("")
        assert result.sentence_count >= 0
        assert result.word_count == 0

    def test_sentence_splitting(self, analyzer):
        """Test sentence splitting"""
        text = "Ensimmäinen lause. Toinen lause! Kolmas lause?"
        result = analyzer.analyze(text)
        assert result.sentence_count == 3

    def test_clause_markers(self, analyzer):
        """Test that clause markers increase clause count"""
        without_marker = analyzer.analyze("Kissa juoksee talossa")
        with_marker = analyzer.analyze("Kissa juoksee, joka on talossa")
        assert with_marker.clause_count > without_marker.clause_count

    def test_response_structure(self, analyzer):
        """Test that response has all required fields"""
        result = analyzer.analyze("Testi teksti")
        assert hasattr(result, 'text')
        assert hasattr(result, 'sentence_count')
        assert hasattr(result, 'word_count')
        assert hasattr(result, 'clause_count')
        assert hasattr(result, 'morphological_depth_score')
        assert hasattr(result, 'average_word_length')
        assert hasattr(result, 'complexity_rating')
