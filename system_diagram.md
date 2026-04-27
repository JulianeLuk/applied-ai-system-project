# System Diagram — AI Music Recommender

## Architecture Overview

```
╔══════════════════════════════════════════════════════════════════════════╗
║                        USER INTERFACES (Input)                          ║
║                                                                          ║
║   ┌─────────────────────────┐     ┌──────────────────────────────────┐  ║
║   │    CLI  (src/main.py)   │     │   Streamlit Web App  (app.py)    │  ║
║   │  5 preset test profiles │     │  Sliders: genre, mood, energy,   │  ║
║   │  (pop, lofi, rock, etc) │     │  acoustics, # of results (1-5)   │  ║
║   └────────────┬────────────┘     └────────────────┬─────────────────┘  ║
╚════════════════╪════════════════════════════════════╪════════════════════╝
                 │  UserProfile                       │  UserProfile
                 │  (genre, mood,                     │  + input validation
                 │   energy, acoustic)                │  (guardrails)
                 └─────────────────┬──────────────────┘
                                   ▼
╔══════════════════════════════════════════════════════════════════════════╗
║                         DATA LAYER                                       ║
║                                                                          ║
║   ┌──────────────────────────────────────────────────────────────────┐  ║
║   │                   data/songs.csv  (19 songs)                     │  ║
║   │  Fields: title, artist, genre, mood, energy, tempo, valence,     │  ║
║   │          danceability, acousticness  (numeric: 0.0–1.0)          │  ║
║   └──────────────────────────────┬───────────────────────────────────┘  ║
║                                  │ load_songs()                          ║
║                                  │ (parses CSV → List[Dict],            ║
║                                  │  logs & skips malformed rows)         ║
╚══════════════════════════════════╪═══════════════════════════════════════╝
                                   ▼
╔══════════════════════════════════════════════════════════════════════════╗
║                   RECOMMENDER ENGINE  (src/recommender.py)               ║
║                                                                          ║
║   score_song(user_prefs, song)  →  score [0.0 – 7.0] + reasons list     ║
║                                                                          ║
║   ┌──────────────┐  ┌──────────────┐  ┌───────────┐  ┌───────────────┐ ║
║   │ Genre match  │  │  Mood match  │  │  Energy   │  │ Acoustic pref │ ║
║   │   +2.0 pts   │  │   +1.5 pts   │  │ +2.0 pts  │  │   +1.0 pts    │ ║
║   │ (categorical)│  │ (categorical)│  │(distance) │  │  (boolean)    │ ║
║   └──────────────┘  └──────────────┘  └───────────┘  └───────────────┘ ║
║                                              +  Valence bonus (+0.5)     ║
║                                                                          ║
║   recommend_songs(user_prefs, songs, k)                                  ║
║       → scores all 19 songs → sorts descending → returns top-k          ║
║         results: [(song_dict, score, reasons), ...]                      ║
╚══════════════════════════════════╪═══════════════════════════════════════╝
                                   │  top-k results
                     ┌─────────────┴──────────────┐
                     │                            │
                     ▼                            ▼
╔═══════════════════════════╗    ╔════════════════════════════════════════╗
║   CLI OUTPUT              ║    ║   RAG EXPLAINER  (src/ai_explainer.py) ║
║                           ║    ║                                        ║
║  Formatted table:         ║    ║  RETRIEVE: top-k scored songs          ║
║  rank │ title │ artist    ║    ║      ↓                                  ║
║  genre │ score │ reasons  ║    ║  AUGMENT: _format_song_context()       ║
║                           ║    ║    (song title, genre, energy, score   ║
╚═══════════════════════════╝    ║     → text block for LLM prompt)       ║
                                 ║      ↓                                  ║
                                 ║  GENERATE: OpenRouter API              ║
                                 ║    Model: GPT-OSS-120B                 ║
                                 ║    → 2-3 sentence friendly explanation ║
                                 ║    → fallback msg if no API key        ║
                                 ╚══════════════╪═════════════════════════╝
                                                │ AI explanation text
                                                ▼
╔══════════════════════════════════════════════════════════════════════════╗
║                      STREAMLIT OUTPUT (app.py)                           ║
║                                                                          ║
║   Top-k song cards, each showing:                                        ║
║   • Song title, artist, genre, mood                                      ║
║   • Numeric score  +  rule-based reasoning breakdown                     ║
║   • AI-generated explanation (info box)                                  ║
║                                                                          ║
║   Logging → logs/app.log  (user requests, API errors, completions)       ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## Human Review & Testing Layer

```
╔══════════════════════════════════════════════════════════════════════════╗
║                    TESTING & HUMAN EVALUATION                            ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  AUTOMATED TESTS  (pytest)                                               ║
║  ┌────────────────────────────────┐  ┌─────────────────────────────┐    ║
║  │  tests/test_recommender.py     │  │ tests/test_consistency.py   │    ║
║  │  • Top result matches profile  │  │ • Same profile → same #1    ║    ║
║  │  • Explanation is non-empty    │  │   (5 runs, determinism)     │    ║
║  └────────────────────────────────┘  │ • Scores stay in [0, 7]    │    ║
║                                      │ • k=1,3,5 returns exact k  │    ║
║                                      │ • Scores sorted descending │    ║
║                                      │ • Different profiles →     │    ║
║                                      │   different top song       │    ║
║                                      └─────────────────────────────┘    ║
║                                                                          ║
║  HUMAN-IN-THE-LOOP                                                       ║
║  ┌──────────────────────────────────────────────────────────────────┐   ║
║  │  1. Manual inspection via 5 preset CLI profiles                  │   ║
║  │     (human reads table, checks if top song makes sense)          │   ║
║  │                                                                  │   ║
║  │  2. Interactive Streamlit UI                                     │   ║
║  │     (human adjusts sliders → live results → human judges fit)    │   ║
║  │                                                                  │   ║
║  │  3. Bias review (model_card.md)                                  │   ║
║  │     • Cross-profile comparison: genre A vs. genre B              │   ║
║  │     • Identified: genre filter bubble, small dataset skew        │   ║
║  │     • Weight experiment: genre weight 2.0 → 0.5 ↑ diversity      │   ║
║  │                                                                  │   ║
║  │  4. Log review  (logs/app.log)                                   │   ║
║  │     (human audits API errors, unexpected inputs, AI responses)   │   ║
║  └──────────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## Data Flow Summary

```
[User Preferences]
      │
      ▼
[Input Validation]  ←── guardrails reject unknown genres/moods
      │
      ▼
[load_songs]  ←── data/songs.csv  (19 songs, 10 features each)
      │
      ▼
[score_song × 19]  ←── weighted formula (genre+mood+energy+acoustic+valence)
      │                 returns (score, reasons) per song
      ▼
[sort & top-k]  ←── deterministic ranking, 0.0–7.0 scale
      │
      ├──→ [CLI table]  (human reads rank/score/reasons)
      │
      └──→ [RAG Explainer]
                │  retrieve: top-k results
                │  augment: format as prompt context
                │  generate: LLM → friendly explanation
                ▼
           [Streamlit UI]  (song cards + rule reasons + AI explanation)
                │
                ▼
           [logs/app.log]  (human audit trail)
```
