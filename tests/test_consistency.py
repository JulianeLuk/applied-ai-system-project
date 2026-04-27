"""
Reliability / consistency tests.

These verify that the recommender:
1. Returns the same top song every time for identical inputs (determinism)
2. Produces scores within the expected 0–7.0 range
3. Always returns exactly k results when k <= catalog size
"""

from src.recommender import load_songs, recommend_songs

PROFILE = {
    "genre": "pop",
    "mood": "happy",
    "energy": 0.85,
    "likes_acoustic": False,
}

DATA_PATH = "data/songs.csv"


def test_top_recommendation_is_consistent():
    """Running the same profile 5 times should always produce the same #1 song."""
    songs = load_songs(DATA_PATH)
    top_titles = [recommend_songs(PROFILE, songs, k=3)[0][0]["title"] for _ in range(5)]
    assert len(set(top_titles)) == 1, (
        f"Top recommendation is not consistent across runs: {top_titles}"
    )


def test_score_range():
    """Every score should fall in [0.0, 7.0] — the theoretical max of the scoring formula."""
    songs = load_songs(DATA_PATH)
    results = recommend_songs(PROFILE, songs, k=len(songs))
    for song, score, _ in results:
        assert 0.0 <= score <= 7.0, (
            f"Score {score:.2f} for '{song['title']}' is outside the expected 0–7.0 range"
        )


def test_returns_correct_k():
    """recommend_songs should return exactly k results for k in [1, 3, 5]."""
    songs = load_songs(DATA_PATH)
    for k in [1, 3, 5]:
        results = recommend_songs(PROFILE, songs, k=k)
        assert len(results) == k, f"Expected {k} results, got {len(results)}"


def test_scores_are_sorted_descending():
    """Results must be ordered from highest to lowest score."""
    songs = load_songs(DATA_PATH)
    results = recommend_songs(PROFILE, songs, k=5)
    scores = [score for _, score, _ in results]
    assert scores == sorted(scores, reverse=True), (
        f"Scores are not sorted descending: {scores}"
    )


def test_different_profiles_produce_different_results():
    """Two very different profiles should not return the same top song."""
    songs = load_songs(DATA_PATH)
    pop_top = recommend_songs(
        {"genre": "pop", "mood": "happy", "energy": 0.9, "likes_acoustic": False},
        songs, k=1
    )[0][0]["title"]
    lofi_top = recommend_songs(
        {"genre": "lofi", "mood": "chill", "energy": 0.3, "likes_acoustic": True},
        songs, k=1
    )[0][0]["title"]
    assert pop_top != lofi_top, (
        f"Opposite profiles returned the same top song: '{pop_top}'"
    )
