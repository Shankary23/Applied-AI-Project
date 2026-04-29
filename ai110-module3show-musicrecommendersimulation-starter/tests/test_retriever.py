"""
Tests for the RAG retrieval step (src/retriever.py).

These tests verify that retrieve_candidates:
  - returns the right number of results
  - surfaces more relevant songs than a random draw would
  - handles edge cases like empty genre/mood without crashing
"""

from src.retriever import retrieve_candidates, _song_tags, _query_tags, _jaccard


# ── Shared fixtures ───────────────────────────────────────────────────────────

def make_catalog():
    """Small in-memory catalog that covers multiple genres and energy levels."""
    return [
        {"genre": "lofi",     "mood": "chill",    "energy": 0.35, "danceability": 0.55, "acousticness": 0.85, "title": "Chill Lofi"},
        {"genre": "lofi",     "mood": "focused",  "energy": 0.40, "danceability": 0.60, "acousticness": 0.80, "title": "Study Lofi"},
        {"genre": "pop",      "mood": "happy",    "energy": 0.82, "danceability": 0.80, "acousticness": 0.15, "title": "Pop Banger"},
        {"genre": "metal",    "mood": "intense",  "energy": 0.97, "danceability": 0.45, "acousticness": 0.05, "title": "Metal Riff"},
        {"genre": "jazz",     "mood": "relaxed",  "energy": 0.38, "danceability": 0.52, "acousticness": 0.88, "title": "Jazz Cafe"},
        {"genre": "hip-hop",  "mood": "energetic","energy": 0.88, "danceability": 0.92, "acousticness": 0.06, "title": "Hip Hop Hit"},
        {"genre": "classical","mood": "melancholic","energy": 0.20,"danceability": 0.25, "acousticness": 0.98, "title": "Classical Suite"},
    ]


# ── Test 1: correct candidate count ──────────────────────────────────────────

def test_retrieve_returns_n_candidates():
    """retrieve_candidates should return exactly n songs when n <= catalog size."""
    catalog = make_catalog()
    user = {"genre": "lofi", "mood": "chill", "target_energy": 0.35,
            "target_danceability": 0.55, "target_acousticness": 0.85}

    results = retrieve_candidates(user, catalog, n=3)

    assert len(results) == 3


def test_retrieve_caps_at_catalog_size():
    """retrieve_candidates should not crash or pad when n > catalog size."""
    catalog = make_catalog()
    user = {"genre": "lofi", "mood": "chill", "target_energy": 0.35,
            "target_danceability": 0.55, "target_acousticness": 0.85}

    results = retrieve_candidates(user, catalog, n=100)

    assert len(results) == len(catalog)


# ── Test 2: relevance — retrieved songs match the query better than others ───

def test_retrieve_surfaces_matching_genre():
    """The top retrieval result should match the user's genre when one exists."""
    catalog = make_catalog()
    user = {"genre": "lofi", "mood": "chill", "target_energy": 0.35,
            "target_danceability": 0.55, "target_acousticness": 0.85}

    results = retrieve_candidates(user, catalog, n=3)
    top_genres = [s["genre"] for s in results]

    # At least 2 of the top 3 candidates should be lofi
    assert top_genres.count("lofi") >= 2


def test_retrieve_orders_by_jaccard_similarity():
    """Songs with more tag overlap should rank above songs with less overlap."""
    catalog = make_catalog()
    user = {"genre": "metal", "mood": "intense", "target_energy": 0.95,
            "target_danceability": 0.45, "target_acousticness": 0.05}

    results = retrieve_candidates(user, catalog, n=len(catalog))
    titles = [s["title"] for s in results]

    # Metal Riff should be ranked first — it matches genre, mood, and all buckets
    assert titles[0] == "Metal Riff"


# ── Test 3: edge cases ────────────────────────────────────────────────────────

def test_retrieve_handles_empty_genre_and_mood():
    """An empty genre or mood string should not crash the retriever."""
    catalog = make_catalog()
    user = {"genre": "", "mood": "", "target_energy": 0.50,
            "target_danceability": 0.60, "target_acousticness": 0.50}

    results = retrieve_candidates(user, catalog, n=3)

    # Should still return results — just matched on continuous feature buckets
    assert len(results) == 3


def test_jaccard_perfect_overlap():
    """Two identical sets should produce a Jaccard score of 1.0."""
    tags = {"lofi", "chill", "low_energy", "medium_dance", "high_acoustic"}
    assert _jaccard(tags, tags) == 1.0


def test_jaccard_no_overlap():
    """Two disjoint sets should produce a Jaccard score of 0.0."""
    a = {"lofi", "chill"}
    b = {"metal", "intense"}
    assert _jaccard(a, b) == 0.0


def test_jaccard_empty_sets():
    """Two empty sets should return 0.0 without raising ZeroDivisionError."""
    assert _jaccard(set(), set()) == 0.0
