"""
RAG Retrieval Module
====================
This module implements the **Retrieve** step of the RAG pipeline.

RAG stands for Retrieval-Augmented Generation. The idea is:
  1. RETRIEVE  — quickly narrow a large catalog down to the most relevant candidates.
  2. RANK/SCORE — run the more expensive weighted scoring only on those candidates.

Without retrieval, recommend_songs scores every song in the catalog.
With retrieval, it first picks the 15 most tag-similar songs, then scores just those.
As the catalog grows (hundreds or thousands of songs), this saves real time
and also tends to surface better results by filtering out clearly irrelevant songs first.

How retrieval works here
------------------------
Each song is described by a small set of **tags**:
  - its genre (e.g. "lofi")
  - its mood  (e.g. "chill")
  - its energy level bucket ("low", "medium", or "high" energy)
  - its danceability bucket
  - its acousticness bucket

The user's preferences are converted into the same tag format.
Songs are then ranked by **Jaccard similarity** — the fraction of tags they share
with the user's query. The top N songs become the candidate shortlist.
"""

from typing import Dict, List, Set


# ── Tag helpers ───────────────────────────────────────────────────────────────

def _energy_bucket(val: float) -> str:
    """Map a 0-1 energy value to a coarse label used for tag matching."""
    if val < 0.35:
        return "very_low_energy"
    if val < 0.55:
        return "low_energy"
    if val < 0.70:
        return "medium_energy"
    if val < 0.85:
        return "high_energy"
    return "very_high_energy"


def _dance_bucket(val: float) -> str:
    if val < 0.40:
        return "low_dance"
    if val < 0.65:
        return "medium_dance"
    return "high_dance"


def _acoustic_bucket(val: float) -> str:
    if val < 0.35:
        return "low_acoustic"
    if val < 0.65:
        return "medium_acoustic"
    return "high_acoustic"


def _song_tags(song: Dict) -> Set[str]:
    """Convert a song dictionary into a set of descriptive tags."""
    return {
        song["genre"].lower(),
        song["mood"].lower(),
        _energy_bucket(song["energy"]),
        _dance_bucket(song["danceability"]),
        _acoustic_bucket(song["acousticness"]),
    }


def _query_tags(user_prefs: Dict) -> Set[str]:
    """Convert user preferences into the same tag format as songs."""
    tags = {
        _energy_bucket(user_prefs["target_energy"]),
        _dance_bucket(user_prefs["target_danceability"]),
        _acoustic_bucket(user_prefs["target_acousticness"]),
    }
    if user_prefs.get("genre"):
        tags.add(user_prefs["genre"].lower())
    if user_prefs.get("mood"):
        tags.add(user_prefs["mood"].lower())
    return tags


# ── Jaccard similarity ────────────────────────────────────────────────────────

def _jaccard(a: Set[str], b: Set[str]) -> float:
    """
    Jaccard similarity = |intersection| / |union|.
    Returns 0.0 when both sets are empty to avoid division by zero.
    Range is 0.0 (no overlap) to 1.0 (identical sets).
    """
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


# ── Public API ────────────────────────────────────────────────────────────────

def retrieve_candidates(user_prefs: Dict, songs: List[Dict], n: int = 15) -> List[Dict]:
    """
    RAG Step 1 — Retrieve the top n candidate songs for a user's preferences.

    Ranks every song by Jaccard similarity between its tags and the user's
    query tags, then returns the n highest-scoring songs as a shortlist.
    The scoring step in recommend_songs then operates only on this shortlist.

    Parameters
    ----------
    user_prefs : dict  — keys: genre, mood, target_energy, target_danceability,
                         target_acousticness
    songs      : list  — all songs loaded from songs.csv
    n          : int   — how many candidates to return (default 15)

    Returns
    -------
    List of up to n song dicts, sorted by descending tag similarity.
    """
    query = _query_tags(user_prefs)
    ranked = sorted(
        songs,
        key=lambda song: _jaccard(query, _song_tags(song)),
        reverse=True,
    )
    return ranked[:n]
