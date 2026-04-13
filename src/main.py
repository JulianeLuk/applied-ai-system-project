"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from tabulate import tabulate

from src.recommender import load_songs, recommend_songs


def print_recommendations(user_prefs, songs, profile_name):
    """Helper to print recommendations for a given profile."""
    recommendations = recommend_songs(user_prefs, songs, k=3)
    
    print(f"\n{'='*60}")
    print(f"Profile: {profile_name}")
    print(f"Preferences: {user_prefs}")
    print(f"{'='*60}\n")

    table_rows = []
    for i, rec in enumerate(recommendations, 1):
        song, score, reasons = rec
        if isinstance(reasons, list):
            explanation = "; ".join(reasons)
        else:
            explanation = str(reasons)

        table_rows.append(
            [
                i,
                song["title"],
                song["artist"],
                song["genre"],
                song["mood"],
                f"{score:.2f}",
                explanation,
            ]
        )

    headers = ["#", "Title", "Artist", "Genre", "Mood", "Score", "Reasons"]
    max_widths = [3, 24, 18, 12, 12, 8, 56]

    print(
        tabulate(
            table_rows,
            headers=headers,
            tablefmt="fancy_grid",
            maxcolwidths=max_widths,
        )
    )

    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    
    # Test profiles
    profiles = [
        {
            "name": "High-Energy Pop",
            "prefs": {"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": False}
        },
        {
            "name": "Chill Lofi",
            "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True}
        },
        {
            "name": "Deep Intense Rock",
            "prefs": {"genre": "rock", "mood": "intense", "energy": 0.90, "likes_acoustic": False}
        },
        {
            "name": "Ambient Chill Acoustic",
            "prefs": {"genre": "ambient", "mood": "chill", "energy": 0.30, "likes_acoustic": True}
        },
        {
            "name": "Jazz Relaxed Mid-Energy",
            "prefs": {"genre": "jazz", "mood": "relaxed", "energy": 0.50, "likes_acoustic": True}
        },
    ]
    
    for profile in profiles:
        print_recommendations(profile["prefs"], songs, profile["name"])


if __name__ == "__main__":
    main()
