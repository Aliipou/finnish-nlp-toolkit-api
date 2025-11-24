"""
Integration tests for API endpoints
Tests the full API functionality end-to-end
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestAPIIntegration:
    """Integration tests for all API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    # System Endpoints Tests
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_version_endpoint(self, client):
        """Test version endpoint"""
        response = client.get("/version")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "api" in data

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data

    # Lemmatization Endpoint Tests
    def test_lemmatize_post(self, client):
        """Test lemmatization POST endpoint"""
        payload = {
            "text": "Kissani söi hiiren nopeasti",
            "include_morphology": True
        }
        response = client.post("/api/lemmatize", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "lemmas" in data
        assert "word_count" in data
        assert data["word_count"] > 0
        assert len(data["lemmas"]) > 0

    def test_lemmatize_get(self, client):
        """Test lemmatization GET endpoint"""
        response = client.get("/api/lemmatize?text=kissa juoksee")
        assert response.status_code == 200
        data = response.json()
        assert "lemmas" in data
        assert data["word_count"] == 2

    def test_lemmatize_with_morphology(self, client):
        """Test lemmatization with morphology"""
        response = client.get("/api/lemmatize?text=kissalla&include_morphology=true")
        assert response.status_code == 200
        data = response.json()
        assert data["lemmas"][0]["morphology"] is not None

    def test_lemmatize_without_morphology(self, client):
        """Test lemmatization without morphology"""
        response = client.get("/api/lemmatize?text=kissalla&include_morphology=false")
        assert response.status_code == 200
        data = response.json()
        assert data["lemmas"][0]["morphology"] is None

    def test_lemmatize_empty_text(self, client):
        """Test lemmatization with empty text should fail validation"""
        payload = {"text": "", "include_morphology": True}
        response = client.post("/api/lemmatize", json=payload)
        assert response.status_code == 422  # Validation error

    # Complexity Analysis Endpoint Tests
    def test_complexity_post(self, client):
        """Test complexity analysis POST endpoint"""
        payload = {
            "text": "Kissa, joka söi hiiren, juoksi nopeasti.",
            "detailed": True
        }
        response = client.post("/api/complexity", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "sentence_count" in data
        assert "word_count" in data
        assert "clause_count" in data
        assert "morphological_depth_score" in data
        assert "complexity_rating" in data

    def test_complexity_get(self, client):
        """Test complexity analysis GET endpoint"""
        response = client.get("/api/complexity?text=Kissa juoksee")
        assert response.status_code == 200
        data = response.json()
        assert data["word_count"] == 2
        assert data["sentence_count"] >= 1

    def test_complexity_detailed(self, client):
        """Test complexity analysis with detailed=True"""
        response = client.get("/api/complexity?text=Talossa on kissa&detailed=true")
        assert response.status_code == 200
        data = response.json()
        assert data["case_distribution"] is not None
        assert "nominative" in data["case_distribution"]

    def test_complexity_not_detailed(self, client):
        """Test complexity analysis with detailed=False"""
        response = client.get("/api/complexity?text=Talossa on kissa&detailed=false")
        assert response.status_code == 200
        data = response.json()
        assert data["case_distribution"] is None

    def test_complexity_rating(self, client):
        """Test that complexity rating is valid"""
        response = client.get("/api/complexity?text=Kissa juoksee")
        assert response.status_code == 200
        data = response.json()
        assert data["complexity_rating"] in ["Simple", "Moderate", "Complex"]

    # Profanity Detection Endpoint Tests
    def test_profanity_post(self, client):
        """Test profanity detection POST endpoint"""
        payload = {
            "text": "Tämä on testi teksti",
            "return_flagged_words": False,
            "threshold": 0.5
        }
        response = client.post("/api/swear-check", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "is_toxic" in data
        assert "toxicity_score" in data
        assert "severity" in data

    def test_profanity_get(self, client):
        """Test profanity detection GET endpoint"""
        response = client.get("/api/swear-check?text=Hei maailma")
        assert response.status_code == 200
        data = response.json()
        assert data["is_toxic"] is False

    def test_profanity_with_flagged_words(self, client):
        """Test profanity detection with flagged words"""
        response = client.get("/api/swear-check?text=vittu&return_flagged_words=true")
        assert response.status_code == 200
        data = response.json()
        assert data["is_toxic"] is True
        if data["flagged_words"]:
            assert len(data["flagged_words"]) > 0

    def test_profanity_without_flagged_words(self, client):
        """Test profanity detection without flagged words"""
        response = client.get("/api/swear-check?text=vittu&return_flagged_words=false")
        assert response.status_code == 200
        data = response.json()
        assert data["flagged_words"] is None

    def test_profanity_threshold(self, client):
        """Test profanity detection with custom threshold"""
        response = client.get("/api/swear-check?text=hitto&threshold=0.1")
        assert response.status_code == 200
        data = response.json()
        # With low threshold, should be detected
        assert isinstance(data["is_toxic"], bool)

    def test_profanity_severity(self, client):
        """Test that severity is valid"""
        response = client.get("/api/swear-check?text=test")
        assert response.status_code == 200
        data = response.json()
        assert data["severity"] in ["None", "Low", "Medium", "High"]

    # Cross-functionality Tests
    def test_all_endpoints_with_same_text(self, client):
        """Test all endpoints with the same text"""
        text = "Kissa juoksi talossa nopeasti"

        # Lemmatize
        lem_response = client.get(f"/api/lemmatize?text={text}")
        assert lem_response.status_code == 200

        # Complexity
        comp_response = client.get(f"/api/complexity?text={text}")
        assert comp_response.status_code == 200

        # Profanity
        prof_response = client.get(f"/api/swear-check?text={text}")
        assert prof_response.status_code == 200

        # All should return data
        assert lem_response.json()["word_count"] > 0
        assert comp_response.json()["word_count"] > 0
        assert prof_response.json()["is_toxic"] is False

    def test_long_text_handling(self, client):
        """Test API handling of longer text"""
        long_text = " ".join(["Kissa juoksee"] * 50)

        # Should handle long text
        response = client.get(f"/api/complexity?text={long_text}")
        assert response.status_code == 200

    def test_special_characters(self, client):
        """Test handling of special characters"""
        text = "Kissa! Koira? Lintu... öäå"
        response = client.get(f"/api/lemmatize?text={text}")
        assert response.status_code == 200

    def test_concurrent_requests(self, client):
        """Test multiple concurrent requests"""
        texts = [
            "kissa",
            "koira",
            "lintu",
            "auto",
            "talo"
        ]

        responses = []
        for text in texts:
            response = client.get(f"/api/lemmatize?text={text}")
            responses.append(response)

        # All should succeed
        assert all(r.status_code == 200 for r in responses)

    def test_api_documentation(self, client):
        """Test that API documentation is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema(self, client):
        """Test that OpenAPI schema is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema
