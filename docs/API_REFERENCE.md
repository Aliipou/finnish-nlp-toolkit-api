# API Reference

Complete reference for the Finnish NLP Toolkit API.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

Currently no authentication required. For production, consider implementing API keys or OAuth.

---

## System Endpoints

### Health Check

Check if the API is running and healthy.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "service": "Finnish NLP Toolkit API"
}
```

**Status Codes**:
- `200 OK`: Service is healthy
- `503 Service Unavailable`: Service is down

---

### Version Information

Get API version details.

**Endpoint**: `GET /version`

**Response**:
```json
{
  "version": "1.0.0",
  "api": "Finnish NLP Toolkit",
  "python_version": "3.11.0"
}
```

---

## Lemmatization API

### Lemmatize Text (POST)

Lemmatize Finnish text with morphological analysis.

**Endpoint**: `POST /api/lemmatize`

**Request Body**:
```json
{
  "text": "Kissani söi hiiren nopeasti",
  "include_morphology": true
}
```

**Parameters**:
- `text` (string, required): Finnish text to lemmatize (1-10000 characters)
- `include_morphology` (boolean, optional): Include morphological features (default: true)

**Response**:
```json
{
  "text": "Kissani söi hiiren nopeasti",
  "lemmas": [
    {
      "original": "Kissani",
      "lemma": "kissa",
      "pos": "NOUN",
      "morphology": {
        "case": "Nominative",
        "number": "Singular"
      }
    },
    {
      "original": "söi",
      "lemma": "syödä",
      "pos": "VERB",
      "morphology": {
        "case": "Nominative",
        "number": "Singular"
      }
    }
  ],
  "word_count": 4
}
```

**Status Codes**:
- `200 OK`: Success
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Processing error

---

### Lemmatize Text (GET)

Simple lemmatization via query parameters.

**Endpoint**: `GET /api/lemmatize`

**Query Parameters**:
- `text` (string, required): Text to lemmatize
- `include_morphology` (boolean, optional): Include morphology (default: true)

**Example**:
```bash
GET /api/lemmatize?text=kissa%20juoksee&include_morphology=true
```

---

## Complexity Analysis API

### Analyze Complexity (POST)

Analyze linguistic complexity of Finnish text.

**Endpoint**: `POST /api/complexity`

**Request Body**:
```json
{
  "text": "Kissa, joka söi hiiren, juoksi nopeasti puutarhaan.",
  "detailed": true
}
```

**Parameters**:
- `text` (string, required): Text to analyze (1-10000 characters)
- `detailed` (boolean, optional): Include detailed metrics (default: true)

**Response**:
```json
{
  "text": "Kissa, joka söi hiiren, juoksi nopeasti puutarhaan.",
  "sentence_count": 1,
  "word_count": 7,
  "clause_count": 3,
  "morphological_depth_score": 48.5,
  "average_word_length": 6.14,
  "case_distribution": {
    "nominative": 3,
    "genitive": 1,
    "partitive": 0,
    "inessive": 0,
    "elative": 0,
    "illative": 1,
    "adessive": 0,
    "ablative": 0,
    "allative": 0,
    "essive": 0,
    "translative": 0,
    "other": 0
  },
  "complexity_rating": "Moderate"
}
```

**Complexity Ratings**:
- `Simple`: Low morphological depth, few clauses
- `Moderate`: Medium complexity
- `Complex`: High morphological depth, many clauses

**Status Codes**:
- `200 OK`: Success
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Processing error

---

### Analyze Complexity (GET)

Analyze via query parameters.

**Endpoint**: `GET /api/complexity`

**Query Parameters**:
- `text` (string, required): Text to analyze
- `detailed` (boolean, optional): Include details (default: true)

**Example**:
```bash
GET /api/complexity?text=Kissa%20juoksee&detailed=true
```

---

## Profanity Detection API

### Check Profanity (POST)

Detect profanity and toxicity in text.

**Endpoint**: `POST /api/swear-check`

**Request Body**:
```json
{
  "text": "Tämä on testi teksti",
  "return_flagged_words": true,
  "threshold": 0.5
}
```

**Parameters**:
- `text` (string, required): Text to check (1-10000 characters)
- `return_flagged_words` (boolean, optional): Return flagged words list (default: false)
- `threshold` (float, optional): Detection threshold 0.0-1.0 (default: 0.5)

**Response**:
```json
{
  "text": "Tämä on testi teksti",
  "is_toxic": false,
  "toxicity_score": 0.0,
  "severity": "None",
  "flagged_words": null
}
```

**With Flagged Words**:
```json
{
  "text": "vittu paska",
  "is_toxic": true,
  "toxicity_score": 0.75,
  "severity": "High",
  "flagged_words": [
    {
      "word": "vittu",
      "position": 0,
      "confidence": 0.8
    },
    {
      "word": "paska",
      "position": 6,
      "confidence": 0.6
    }
  ]
}
```

**Severity Levels**:
- `None`: No toxicity detected
- `Low`: Mild profanity (0.2-0.4)
- `Medium`: Moderate profanity (0.4-0.7)
- `High`: Strong profanity (0.7+)

**Status Codes**:
- `200 OK`: Success
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Processing error

---

## Error Responses

All endpoints may return error responses in this format:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE"
}
```

**Common Error Codes**:
- `422`: Validation error (invalid input)
- `500`: Internal server error
- `503`: Service unavailable

---

## Rate Limiting

Currently no rate limiting. For production deployment, consider implementing:
- Per-IP rate limiting
- API key-based quotas
- Request throttling

---

## CORS

CORS is enabled for all origins in development. Configure `CORS_ORIGINS` environment variable for production.

---

## Examples

### Python

```python
import requests

# Lemmatization
response = requests.get(
    "http://localhost:8000/api/lemmatize",
    params={"text": "kissani söi hiiren", "include_morphology": True}
)
data = response.json()
print(f"Lemmas: {data['lemmas']}")

# Complexity
response = requests.post(
    "http://localhost:8000/api/complexity",
    json={"text": "Kissa juoksi nopeasti", "detailed": True}
)
data = response.json()
print(f"Complexity: {data['complexity_rating']}")

# Profanity
response = requests.get(
    "http://localhost:8000/api/swear-check",
    params={"text": "puhdas teksti", "threshold": 0.5}
)
data = response.json()
print(f"Is toxic: {data['is_toxic']}")
```

### JavaScript

```javascript
// Lemmatization
fetch('http://localhost:8000/api/lemmatize?text=kissa+juoksee')
  .then(response => response.json())
  .then(data => console.log('Lemmas:', data.lemmas));

// Complexity
fetch('http://localhost:8000/api/complexity', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    text: 'Kissa juoksi nopeasti',
    detailed: true
  })
})
  .then(response => response.json())
  .then(data => console.log('Complexity:', data.complexity_rating));

// Profanity
fetch('http://localhost:8000/api/swear-check?text=puhdas+teksti')
  .then(response => response.json())
  .then(data => console.log('Is toxic:', data.is_toxic));
```

### cURL

```bash
# Lemmatization
curl -X GET "http://localhost:8000/api/lemmatize?text=kissa+juoksee&include_morphology=true"

# Complexity
curl -X POST "http://localhost:8000/api/complexity" \
  -H "Content-Type: application/json" \
  -d '{"text": "Kissa juoksi nopeasti", "detailed": true}'

# Profanity
curl -X GET "http://localhost:8000/api/swear-check?text=puhdas+teksti&threshold=0.5"
```

---

## Interactive Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json
