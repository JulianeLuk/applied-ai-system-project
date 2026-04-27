# MUSE — AI Music Recommender

A rule-based music recommendation engine augmented with a Retrieval-Augmented Generation (RAG) explainer and a Streamlit web interface. 

## Loom Link 
https://www.loom.com/share/cb981dbe270e489a9bec4e11f4056498 
---

## Original Project (Modules 3)

The foundation of this project was the **Music Recommender Simulation**, a pure rule-based system with no AI or graphical interface. Its goal was to represent songs and a user "taste profile" as structured data, design a weighted scoring function to match songs to preferences, and evaluate where that logic succeeded or failed. The system scored each song across five features (genre, mood, energy, acousticness, and valence), ranked all songs by score, and printed a formatted table of the top results to the terminal. It demonstrated how real-world recommenders reduce human taste to numeric signals — and how small design choices like feature weighting can create bias.

---

## What This Project Does and Why It Matters

MUSE takes a user's music preferences (genre, mood, energy level, and acoustic taste) and recommends the best-matching songs from a curated catalog. What makes it different from the original simulation is a two-layer output:

1. **Rule-based scoring** — transparent, auditable reasons for every recommendation
2. **AI-generated explanation** — a friendly 2–3 sentence natural language summary powered by an LLM via OpenRouter

 MUSE is designed to be explainable: every result comes with a numeric score, a breakdown of why it matched, and a human-readable AI narrative. It demonstrates how rule-based logic and generative AI can work together rather than replace each other.

---

## Architecture Overview

The system has four layers:

**1. Input Layer** — Two interfaces feed the same recommendation engine:
- `src/main.py` (CLI): runs five preset user profiles automatically
- `app.py` (Streamlit): interactive sidebar with dropdowns, sliders, and a submit button

**2. Data Layer** — `data/songs.csv` holds 19 songs with 10 features each (title, artist, genre, mood, energy, tempo, valence, danceability, acousticness). `load_songs()` parses this CSV and skips malformed rows.

**3. Recommender Engine** (`src/recommender.py`) — `score_song()` computes a compatibility score (0–7.0) for each song using weighted rules:
- Genre match: +2.0 pts
- Mood match: +1.5 pts
- Energy closeness: up to +2.0 pts
- Acoustic preference: +1.0 pts
- Valence bonus: up to +0.5 pts

`recommend_songs()` scores all 19 songs, sorts them, and returns the top k.

**4. RAG Explainer** (`src/ai_explainer.py`) — implements Retrieval-Augmented Generation:
- **Retrieve**: the top-k scored songs from the recommender
- **Augment**: formats song metadata + scores into a structured prompt context
- **Generate**: sends the prompt to an LLM via OpenRouter and returns a conversational explanation

All activity is logged to `logs/app.log`.

See [`system_diagram.md`](system_diagram.md) for the full ASCII architecture diagram.

---

## Setup Instructions

**Prerequisites:** Python 3.10+, pip

**1. Clone the repository**

```bash
git clone <your-repo-url>
cd applied-ai-system-project
```

**2. Create and activate a virtual environment**

```bash
python -m venv .venv

# Mac / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure your API key**

Create a `.env` file in the project root:

```
OPENROUTER_API_KEY=your_key_here
```

Get a free key at [openrouter.ai](https://openrouter.ai). If no key is set, the app still works — the AI explanation panel shows a fallback message and all rule-based results display normally.

**5a. Run the CLI version**

```bash
python -m src.main
```

This runs five preset profiles (High-Energy Pop, Chill Lofi, Deep Intense Rock, Ambient Chill, Jazz Relaxed) and prints a ranked table for each.

**5b. Run the Streamlit web app**

```bash
streamlit run app.py
```

Open browser. Use the sidebar to select your genre, mood, energy level, acoustic preference, and number of results, then click **Get Recommendations**.

**6. Run the test suite**

```bash
pytest
```

---

## Sample Interactions

### Example 1 — High-Energy Pop (CLI)

**Input profile:**
```python
{"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": False}
```

**Top recommendation output:**
```
# | Title             | Artist         | Genre | Mood  | Score | Reasons
1 | Neon Lights       | Test Artist    | pop   | happy | 6.80  | genre match; mood match; high energy match; non-acoustic match
2 | Dance Floor Fever | Test Artist    | pop   | happy | 6.20  | genre match; mood match; energy close
3 | Midnight Pop Hit  | Test Artist    | pop   | chill | 4.10  | genre match; energy close
```

### Example 2 — Chill Lofi (Streamlit)

**Input:** Genre: lofi | Mood: chill | Energy: 0.35 | Acoustic: Yes | Results: 3

**Song cards displayed:**
- "Late Night Study" — lofi, chill, energy 0.30, acousticness 0.85 | Score: 6.50
- "Rainy Afternoon" — lofi, relaxed, energy 0.40, acousticness 0.78 | Score: 5.20
- "Soft Focus" — ambient, chill, energy 0.25, acousticness 0.90 | Score: 4.60

**AI Insight (generated by LLM):**
> "These picks are a perfect match for your chill lofi taste. All three tracks share your preference for low energy and acoustic textures, with 'Late Night Study' hitting closest to your target energy of 0.35. The ambient pick rounds things out with an extra-soft sound for a calm, focused listening session."

### Example 3 — Jazz Relaxed (CLI)

**Input profile:**
```python
{"genre": "jazz", "mood": "relaxed", "energy": 0.50, "likes_acoustic": True}
```

**Result:** Top songs are jazz and acoustic-leaning tracks with mid-range energy. Non-matching genres (rock, synthwave) rank near the bottom of the list.

---

## Design Decisions

**Why rule-based scoring + LLM, not just one or the other?**
A pure LLM can hallucinate or ignore catalog constraints. A pure rule engine can't explain itself warmly to a user. Combining them gives transparency (the score and reasons are always deterministic and auditable) while adding a natural language layer that makes results feel personalized rather than mechanical.

**Why OpenRouter instead of a direct model API?**
OpenRouter provides access to multiple models through one OpenAI-compatible endpoint, making it easy to swap models without changing code. The free-tier `gpt-oss-120b` model was sufficient for 2–3 sentence explanations at no cost.

**Why Streamlit for the UI?**
Streamlit lets you build a functional web interface in Python with almost no frontend code. For a course project where the goal is demonstrating the AI system rather than shipping a product, it keeps the focus on the logic rather than HTML/CSS.

**Why keep genre weight at 2.0 (the highest)?**
Genre is the strongest identity signal in music taste — most users will reject songs outside their preferred genre even if every other feature matches. Higher genre weight reflects that reality. The trade-off is a mild filter bubble, which is explicitly acknowledged in the model card.

**Guardrails:** The Streamlit app validates inputs before scoring. Unknown genres or moods return an error instead of silently producing meaningless results.

---

## Testing Summary

**What worked:**
- All five consistency tests in `test_consistency.py` pass: the same profile always returns the same top song, scores stay within 0–7.0, `k` results are always returned, results are sorted descending, and different profiles produce different top songs.
- The two unit tests in `test_recommender.py` confirm that the pop/happy profile surfaces a pop/happy song first and that explanations are non-empty strings.
- The Streamlit app renders correctly with and without an API key configured.

**What didn't work / limitations discovered:**
- The scoring function can produce ties when two songs are nearly identical. Tie-breaking is currently positional (CSV order), which is acceptable for a demo but would need a secondary sort key in production.
- With only 19 songs in the catalog, rare genres like synthwave sometimes return only one strong match and two weaker fallback songs regardless of preference.
- The LLM occasionally generates generic text that could apply to any recommendation set when the matched songs are very similar to each other. Adding more variety to the catalog would improve explanation specificity.

**What I learned:**
Testing a recommender is not just about checking function outputs  it's about checking system behavior across inputs. The consistency tests were more revealing than the unit tests because they caught a sorting-stability issue that unit tests would have missed.

---

## Reflection

This project showed me that building an AI system is really a series of design decisions, each with a measurable trade-off. Choosing the genre weight, deciding what counts as a "close" energy match, picking how many sentences the LLM should write — none of these have a single right answer. They all depend on what you are optimizing for and who the system is serving.

The RAG pattern was the most interesting part to implement. Before this project, I thought of AI as either "it knows the answer" or "it doesn't." RAG changed that: the LLM doesn't need to know your music catalog — it just needs to read the context you hand it and synthesize something useful. That mental model feels broadly applicable well beyond music recommendation.

The part that surprised me most was how quickly bias appears. Genre reinforcement, acoustic overrepresentation, and small-catalog skew all showed up without me deliberately building them in. Real systems deal with these problems at a scale where human inspection is impossible, which makes fairness tooling and diverse dataset curation genuinely hard engineering problems rather than afterthoughts.
