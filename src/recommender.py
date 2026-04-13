import csv

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> float:
        """Score a Song dataclass against a UserProfile."""
        score = 0.0

        # Genre match: strongest signal (+2.0)
        if song.genre == user.favorite_genre:
            score += 2.0

        # Mood match (+1.5)
        if song.mood == user.favorite_mood:
            score += 1.5

        # Energy closeness: linear scale, up to +2.0
        energy_diff = abs(song.energy - user.target_energy)
        score += 2.0 * (1.0 - energy_diff)

        # Acoustic preference: +1.0 if it aligns with user's taste
        if user.likes_acoustic:
            score += 1.0 * song.acousticness
        else:
            score += 1.0 * (1.0 - song.acousticness)

        # Valence bonus: upbeat moods prefer high valence (+0.5)
        positive_moods = {"happy", "intense", "focused"}
        if user.favorite_mood in positive_moods:
            score += 0.5 * song.valence
        else:
            # Mellow moods prefer mid-range valence (~0.6)
            score += 0.5 * (1.0 - abs(song.valence - 0.6))

        return score

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        ranked = sorted(self.songs, key=lambda s: self._score(user, s), reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        reasons: List[str] = []

        if song.genre == user.favorite_genre:
            reasons.append(f"matches your favorite genre ({song.genre})")

        if song.mood == user.favorite_mood:
            reasons.append(f"matches your preferred mood ({song.mood})")

        energy_diff = abs(song.energy - user.target_energy)
        if energy_diff <= 0.1:
            reasons.append(f"energy ({song.energy:.2f}) is very close to your target ({user.target_energy:.2f})")
        elif energy_diff <= 0.25:
            reasons.append(f"energy ({song.energy:.2f}) is close to your target ({user.target_energy:.2f})")

        if user.likes_acoustic and song.acousticness >= 0.6:
            reasons.append(f"acoustic sound you enjoy (acousticness: {song.acousticness:.2f})")
        elif not user.likes_acoustic and song.acousticness <= 0.4:
            reasons.append(f"non-acoustic style you prefer (acousticness: {song.acousticness:.2f})")

        if not reasons:
            reasons.append("overall audio features align with your preferences")

        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs: List[Dict] = []

    with open(csv_path, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if not row:
                continue

            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "mood": row["mood"],
                    "energy": float(row["energy"]),
                    "tempo_bpm": float(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                }
            )

    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a song and return its numeric score plus reasoning."""
    reasons: List[str] = []
    score = 0.0

    target_genre = user_prefs.get("genre", "")
    target_mood = user_prefs.get("mood", "")
    target_energy = float(user_prefs.get("energy", 0.5))
    likes_acoustic = user_prefs.get("likes_acoustic", None)  # None = no preference

    # Genre match: strongest signal (+2.0)
    if song.get("genre") == target_genre:
        score += 2.0
        reasons.append("genre match (+2.0)")

    # Mood match (+1.5)
    if song.get("mood") == target_mood:
        score += 1.5
        reasons.append("mood match (+1.5)")

    # Energy closeness: linear scale, up to +2.0
    song_energy = float(song.get("energy", 0.0))
    energy_diff = abs(song_energy - target_energy)
    energy_points = 2.0 * (1.0 - energy_diff)
    score += energy_points
    reasons.append(f"energy match (+{energy_points:.2f})")

    # Acoustic preference: up to +1.0
    acousticness = float(song.get("acousticness", 0.5))
    if likes_acoustic is True:
        acoustic_points = 1.0 * acousticness
        score += acoustic_points
        reasons.append(f"acoustic preference (+{acoustic_points:.2f})")
    elif likes_acoustic is False:
        acoustic_points = 1.0 * (1.0 - acousticness)
        score += acoustic_points
        reasons.append(f"non-acoustic preference (+{acoustic_points:.2f})")

    # Valence bonus: upbeat moods prefer high valence, mellow prefer mid (+0.5)
    valence = float(song.get("valence", 0.5))
    positive_moods = {"happy", "intense", "focused"}
    if target_mood in positive_moods:
        valence_points = 0.5 * valence
        score += valence_points
        if valence_points > 0.2:
            reasons.append(f"upbeat vibe (+{valence_points:.2f})")
    else:
        valence_points = 0.5 * (1.0 - abs(valence - 0.6))
        score += valence_points

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, List[str]]]:
    """Return the top k songs ranked by score with explanations."""
    scored_songs: List[Tuple[Dict, float, List[str]]] = []

    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored_songs.append((song, score, reasons))

    scored_songs.sort(key=lambda item: item[1], reverse=True)
    return scored_songs[:k]
