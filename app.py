"""
Streamlit UI for the AI Music Recommender.

Run with:
    streamlit run app.py
"""

import logging
import os
import sys

from dotenv import load_dotenv

# Use an explicit path so the .env file is found regardless of working directory
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=_env_path)

import streamlit as st

# ---------------------------------------------------------------------------
# Logging — writes to both logs/app.log and the terminal
# ---------------------------------------------------------------------------
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Local imports (after sys.path is set by Streamlit's working directory)
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(__file__))

from src.recommender import load_songs, recommend_songs
from src.ai_explainer import get_ai_explanation

# ---------------------------------------------------------------------------
# Valid values — used for input guardrails
# ---------------------------------------------------------------------------
KNOWN_GENRES = ["pop", "lofi", "rock", "ambient", "jazz", "synthwave", "indie pop"]
KNOWN_MOODS  = ["happy", "chill", "intense", "relaxed", "moody", "focused"]


def validate_inputs(genre: str, mood: str, energy: float) -> list[str]:
    """Return a list of error messages; empty list means inputs are valid."""
    errors = []
    if genre not in KNOWN_GENRES:
        errors.append(f"Unknown genre '{genre}'. Choose from: {', '.join(KNOWN_GENRES)}")
    if mood not in KNOWN_MOODS:
        errors.append(f"Unknown mood '{mood}'. Choose from: {', '.join(KNOWN_MOODS)}")
    if not (0.0 <= energy <= 1.0):
        errors.append("Energy must be between 0.0 and 1.0.")
    return errors


# ---------------------------------------------------------------------------
# Page layout
# ---------------------------------------------------------------------------
st.set_page_config(page_title="AI Music Recommender", page_icon="music")
st.title("AI Music Recommender")
st.write("Describe your mood and we'll find the right songs — then explain why.")

st.divider()

# --- Sidebar inputs ---
with st.sidebar:
    st.header("Your Preferences")
    genre = st.selectbox("Favorite Genre", KNOWN_GENRES)
    mood  = st.selectbox("Favorite Mood",  KNOWN_MOODS)
    energy = st.slider(
        "Energy Level",
        min_value=0.0, max_value=1.0, value=0.5, step=0.05,
        help="0.0 = very calm, 1.0 = very energetic",
    )
    acoustic_choice = st.radio(
        "Acoustic preference",
        ["Yes, I like acoustic", "No, prefer non-acoustic", "No preference"],
    )
    k = st.slider("Number of recommendations", 1, 5, 3)
    submit = st.button("Get Recommendations", type="primary")

# ---------------------------------------------------------------------------
# Main flow — only runs when the button is clicked
# ---------------------------------------------------------------------------
if submit:
    # --- Input validation (guardrail) ---
    errors = validate_inputs(genre, mood, energy)
    if errors:
        for err in errors:
            st.error(err)
        logger.warning("Invalid user input: %s", errors)
        st.stop()

    acoustic_pref = (
        True  if "Yes"  in acoustic_choice else
        False if "No, prefer" in acoustic_choice else
        None
    )

    user_prefs = {
        "genre": genre,
        "mood": mood,
        "energy": energy,
        "likes_acoustic": acoustic_pref,
    }

    logger.info("New recommendation request: %s", user_prefs)

    # --- Load data ---
    try:
        songs = load_songs("data/songs.csv")
        logger.info("Loaded %d songs from data/songs.csv", len(songs))
    except FileNotFoundError:
        st.error("Song database not found. Make sure data/songs.csv exists.")
        logger.error("data/songs.csv not found")
        st.stop()

    # --- Retrieve top songs (RAG step 1: Retrieve) ---
    top_songs = recommend_songs(user_prefs, songs, k=k)
    logger.info(
        "Retrieved top %d songs: %s",
        len(top_songs),
        [s[0]["title"] for s in top_songs],
    )

    # --- Display rule-based results ---
    st.subheader(f"Top {k} Recommendations")
    for i, (song, score, reasons) in enumerate(top_songs, 1):
        reason_text = "; ".join(reasons) if isinstance(reasons, list) else str(reasons)
        with st.expander(f"{i}. {song['title']} — {song['artist']}  |  Score: {score:.2f}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Genre:** {song['genre']}")
                st.write(f"**Mood:** {song['mood']}")
            with col2:
                st.write(f"**Energy:** {song['energy']:.2f}")
                st.write(f"**Acousticness:** {song['acousticness']:.2f}")
            st.caption(f"Why: {reason_text}")

    st.divider()

    # --- Generate AI explanation (RAG steps 2 & 3: Augment + Generate) ---
    st.subheader("AI Insight")
    with st.spinner("Asking Gemini to explain your recommendations..."):
        ai_text = get_ai_explanation(user_prefs, top_songs)

    st.info(ai_text)
    logger.info("Recommendation complete. AI response length: %d chars", len(ai_text))
