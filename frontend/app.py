"""
Finnish NLP Toolkit - Streamlit Frontend
Interactive UI for testing Finnish NLP features
"""
import streamlit as st
import requests
import json
from typing import Dict, Any


# Configuration
API_BASE_URL = "http://localhost:8000/api"

# Page configuration
st.set_page_config(
    page_title="Finnish NLP Toolkit",
    page_icon="🇫🇮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        padding: 1rem;
    }
    .feature-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #c8e6c9;
        padding: 1rem;
        border-radius: 8px;
    }
    .warning-box {
        background-color: #ffecb3;
        padding: 1rem;
        border-radius: 8px;
    }
    .error-box {
        background-color: #ffcdd2;
        padding: 1rem;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)


def check_api_health() -> bool:
    """Check if API is reachable"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def call_lemmatize_api(text: str, include_morphology: bool) -> Dict[str, Any]:
    """Call lemmatization API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/lemmatize",
            params={
                "text": text,
                "include_morphology": include_morphology
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None


def call_complexity_api(text: str, detailed: bool) -> Dict[str, Any]:
    """Call complexity analysis API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/complexity",
            params={
                "text": text,
                "detailed": detailed
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None


def call_profanity_api(text: str, return_flagged_words: bool, threshold: float) -> Dict[str, Any]:
    """Call profanity detection API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/swear-check",
            params={
                "text": text,
                "return_flagged_words": return_flagged_words,
                "threshold": threshold
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None


def main():
    """Main application"""

    # Header
    st.markdown('<h1 class="main-header">🇫🇮 Finnish NLP Toolkit</h1>', unsafe_allow_html=True)
    st.markdown("---")

    # API Health Check
    with st.sidebar:
        st.header("System Status")
        if check_api_health():
            st.success("✅ API Connected")
        else:
            st.error("❌ API Offline")
            st.info("Make sure the FastAPI server is running on http://localhost:8000")

        st.markdown("---")
        st.header("About")
        st.info("""
        This toolkit provides:
        - **Lemmatization**: Extract base forms of Finnish words
        - **Complexity Analysis**: Analyze sentence complexity
        - **Profanity Detection**: Detect toxic content
        """)

    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📝 Lemmatization", "📊 Complexity Analysis", "🚫 Profanity Detection"])

    # TAB 1: Lemmatization
    with tab1:
        st.header("Finnish Text Lemmatization")
        st.markdown("Convert Finnish words to their base forms (lemmas) with morphological analysis.")

        col1, col2 = st.columns([2, 1])

        with col1:
            lemma_text = st.text_area(
                "Enter Finnish text:",
                value="Kissani söi hiiret nopeasti puutarhassa.",
                height=150,
                key="lemma_input"
            )

        with col2:
            include_morphology = st.checkbox("Include morphological analysis", value=True)
            lemma_button = st.button("Lemmatize", type="primary", use_container_width=True)

        if lemma_button and lemma_text:
            with st.spinner("Analyzing..."):
                result = call_lemmatize_api(lemma_text, include_morphology)

                if result:
                    st.success(f"✅ Processed {result['word_count']} words")

                    # Display results
                    st.subheader("Results")

                    # Create results table
                    for lemma_data in result['lemmas']:
                        with st.expander(f"**{lemma_data['original']}** → {lemma_data['lemma']}", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Original:** {lemma_data['original']}")
                                st.write(f"**Lemma:** {lemma_data['lemma']}")
                            with col2:
                                st.write(f"**POS:** {lemma_data.get('pos', 'N/A')}")
                                if include_morphology and lemma_data.get('morphology'):
                                    st.write("**Morphology:**")
                                    for key, value in lemma_data['morphology'].items():
                                        st.write(f"  - {key}: {value}")

    # TAB 2: Complexity Analysis
    with tab2:
        st.header("Sentence Complexity Analysis")
        st.markdown("Analyze the linguistic complexity of Finnish text.")

        col1, col2 = st.columns([2, 1])

        with col1:
            complexity_text = st.text_area(
                "Enter Finnish text:",
                value="Kissa, joka söi hiiren, juoksi nopeasti puutarhaan, koska se pelkäsi koiraa.",
                height=150,
                key="complexity_input"
            )

        with col2:
            detailed = st.checkbox("Detailed analysis", value=True)
            complexity_button = st.button("Analyze Complexity", type="primary", use_container_width=True)

        if complexity_button and complexity_text:
            with st.spinner("Analyzing..."):
                result = call_complexity_api(complexity_text, detailed)

                if result:
                    # Rating banner
                    rating = result['complexity_rating']
                    if rating == "Simple":
                        st.success(f"✅ Complexity: **{rating}**")
                    elif rating == "Moderate":
                        st.warning(f"⚠️ Complexity: **{rating}**")
                    else:
                        st.error(f"🔴 Complexity: **{rating}**")

                    # Metrics
                    st.subheader("Metrics")
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Sentences", result['sentence_count'])
                    with col2:
                        st.metric("Words", result['word_count'])
                    with col3:
                        st.metric("Clauses", result['clause_count'])
                    with col4:
                        st.metric("Avg Word Length", f"{result['average_word_length']:.1f}")

                    # Morphological depth
                    st.subheader("Morphological Depth Score")
                    st.progress(result['morphological_depth_score'] / 100)
                    st.write(f"**Score:** {result['morphological_depth_score']}/100")

                    # Case distribution
                    if detailed and result.get('case_distribution'):
                        st.subheader("Case Distribution")
                        case_dist = result['case_distribution']

                        # Filter non-zero cases
                        cases = {k: v for k, v in case_dist.items() if v > 0}

                        if cases:
                            col1, col2 = st.columns(2)
                            for i, (case, count) in enumerate(cases.items()):
                                if i % 2 == 0:
                                    col1.write(f"**{case.capitalize()}:** {count}")
                                else:
                                    col2.write(f"**{case.capitalize()}:** {count}")
                        else:
                            st.info("No grammatical cases detected")

    # TAB 3: Profanity Detection
    with tab3:
        st.header("Profanity & Toxicity Detection")
        st.markdown("Detect inappropriate or toxic content in Finnish text.")

        col1, col2 = st.columns([2, 1])

        with col1:
            profanity_text = st.text_area(
                "Enter text to check:",
                value="Tämä on puhdas ja ystävällinen teksti.",
                height=150,
                key="profanity_input"
            )

        with col2:
            return_flagged = st.checkbox("Show flagged words", value=True)
            threshold = st.slider("Detection threshold", 0.0, 1.0, 0.5, 0.1)
            profanity_button = st.button("Check Content", type="primary", use_container_width=True)

        if profanity_button and profanity_text:
            with st.spinner("Analyzing..."):
                result = call_profanity_api(profanity_text, return_flagged, threshold)

                if result:
                    # Toxicity status
                    if result['is_toxic']:
                        st.error(f"⚠️ **TOXIC CONTENT DETECTED** - Severity: {result['severity']}")
                    else:
                        st.success("✅ **CLEAN CONTENT** - No toxicity detected")

                    # Toxicity score
                    st.subheader("Toxicity Score")
                    score = result['toxicity_score']
                    st.progress(score)
                    st.write(f"**Score:** {score:.3f} (Threshold: {threshold})")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Severity", result['severity'])
                    with col2:
                        st.metric("Status", "Toxic" if result['is_toxic'] else "Clean")

                    # Flagged words
                    if return_flagged and result.get('flagged_words'):
                        st.subheader("Flagged Words")
                        for word in result['flagged_words']:
                            with st.expander(f"🚫 {word['word']}", expanded=True):
                                st.write(f"**Position:** {word['position']}")
                                st.write(f"**Confidence:** {word['confidence']:.2f}")


if __name__ == "__main__":
    main()
