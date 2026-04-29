from typing import List, Dict, Tuple, Optional
import csv
from dataclasses import dataclass
from retriever import retrieve_candidates

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
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

# ── Weighting constants ──────────────────────────────────────────────────────
# Energy is now the dominant continuous signal: how hard or soft a song hits
# is the most decisive moment-to-moment factor for this experiment.
# Genre and mood are still rewarded on exact match but carry less weight,
# reflecting that near-energy matches matter more than categorical alignment.
# Danceability and acousticness are continuous: a song that is *close*
# to the target still earns most of its points, rewarding near-matches
# rather than punishing them entirely.
WEIGHT_GENRE        = 1.5   # exact match bonus  (was 3.0)
WEIGHT_MOOD         = 1.5   # exact match bonus  (was 2.0)
WEIGHT_ENERGY       = 4.0   # max points, scaled by 1 - |delta|  (was 2.0)
WEIGHT_DANCEABILITY = 1.5   # max points, scaled by 1 - |delta|
WEIGHT_ACOUSTICNESS = 1.5   # max points, scaled by 1 - |delta|
# Total max score: 10.0  (1.5 + 1.5 + 4.0 + 1.5 + 1.5 = 10.0)


def _score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Score a single song against user preferences.

    Algorithm recipe:
      Step 3a — genre match:       +1.5 pts (exact)
      Step 3b — mood match:        +1.5 pts (exact)
      Step 3c — energy proximity:  +0–4.0   (1 − |delta|)
      Step 3d — dance proximity:   +0–1.5   (1 − |delta|)
      Step 3e — acous proximity:   +0–1.5   (1 − |delta|)

    Returns (score, reasons) where reasons is a list of strings,
    one entry per criterion that contributed meaningfully to the score.
    """
    score = 0.0
    reasons: List[str] = []

    # Step 3a — genre (categorical, exact match)
    if song["genre"].lower() == user_prefs["genre"].lower():
        score += WEIGHT_GENRE
        reasons.append(f"genre matches ({song['genre']}): +{WEIGHT_GENRE} pts")

    # Step 3b — mood (categorical, exact match)
    if song["mood"].lower() == user_prefs["mood"].lower():
        score += WEIGHT_MOOD
        reasons.append(f"mood matches ({song['mood']}): +{WEIGHT_MOOD} pts")

    # Step 3c — energy proximity (continuous)
    energy_delta = abs(song["energy"] - user_prefs["target_energy"])
    energy_pts   = WEIGHT_ENERGY * (1 - energy_delta)
    score       += energy_pts
    if energy_delta < 0.15:
        reasons.append(f"energy close match ({song['energy']}): +{round(energy_pts, 2)} pts")

    # Step 3d — danceability proximity (continuous)
    dance_delta = abs(song["danceability"] - user_prefs["target_danceability"])
    dance_pts   = WEIGHT_DANCEABILITY * (1 - dance_delta)
    score      += dance_pts
    if dance_delta < 0.15:
        reasons.append(f"danceability close match ({song['danceability']}): +{round(dance_pts, 2)} pts")

    # Step 3e — acousticness proximity (continuous)
    acous_delta = abs(song["acousticness"] - user_prefs["target_acousticness"])
    acous_pts   = WEIGHT_ACOUSTICNESS * (1 - acous_delta)
    score      += acous_pts
    if acous_delta < 0.15:
        reasons.append(f"acousticness close match ({song['acousticness']}): +{round(acous_pts, 2)} pts")

    if not reasons:
        reasons.append("partial match on continuous features")

    return round(score, 3), reasons


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> float:
        """Return a numeric score for a single song against a UserProfile."""
        score = 0.0
        if song.genre.lower() == user.favorite_genre.lower():
            score += WEIGHT_GENRE
        if song.mood.lower() == user.favorite_mood.lower():
            score += WEIGHT_MOOD
        score += WEIGHT_ENERGY * (1 - abs(song.energy - user.target_energy))
        target_acous = 0.8 if user.likes_acoustic else 0.2
        score += WEIGHT_ACOUSTICNESS * (1 - abs(song.acousticness - target_acous))
        # danceability: no target in UserProfile, use energy as proxy
        score += WEIGHT_DANCEABILITY * (1 - abs(song.danceability - user.target_energy))
        return score

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs ranked by score for the given user."""
        ranked = sorted(self.songs, key=lambda s: self._score(user, s), reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable string explaining why a song was recommended."""
        reasons = []
        if song.genre.lower() == user.favorite_genre.lower():
            reasons.append(f"genre matches your preference for {user.favorite_genre}")
        if song.mood.lower() == user.favorite_mood.lower():
            reasons.append(f"mood matches your preference for {user.favorite_mood}")
        energy_delta = abs(song.energy - user.target_energy)
        if energy_delta < 0.15:
            reasons.append(f"energy level ({song.energy}) is close to your target ({user.target_energy})")
        if not reasons:
            reasons.append("it scored well on continuous features like energy and danceability")
        return "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    int_fields   = {"id", "tempo_bpm"}
    float_fields = {"energy", "valence", "danceability", "acousticness"}

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for field in int_fields:
                row[field] = int(row[field])
            for field in float_fields:
                row[field] = float(row[field])
            songs.append(row)
    return songs


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    RAG-powered recommendation pipeline.

    Step 1 — RETRIEVE (src/retriever.py)
      Tag-match all songs against user preferences using Jaccard similarity.
      Return the top 15 candidates. This narrows the catalog before scoring,
      which matters as the catalog grows and keeps results focused.

    Step 2 — SCORE (this file)
      Run the weighted scoring algorithm only on the 15 candidates.
      Weights (max 10 pts total):
        Genre match        1.5 pts  — categorical, exact
        Mood match         1.5 pts  — categorical, exact
        Energy proximity   4.0 pts  — continuous, 1 - |delta|
        Danceability prox. 1.5 pts  — continuous, 1 - |delta|
        Acousticness prox. 1.5 pts  — continuous, 1 - |delta|
    """
    # RAG Step 1: retrieve top candidates by tag similarity
    candidates = retrieve_candidates(user_prefs, songs, n=min(15, len(songs)))

    # RAG Step 2: score candidates with the weighted algorithm
    scored = sorted(
        [(song, *_score_song(user_prefs, song)) for song in candidates],
        key=lambda item: item[1],
        reverse=True,
    )
    return [(song, score, ", ".join(reasons)) for song, score, reasons in scored[:k]]
