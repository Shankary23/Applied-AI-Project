"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from pathlib import Path
from recommender import load_songs, recommend_songs

DATA_PATH = Path(__file__).parent.parent / "data" / "songs.csv"

def main() -> None:
    songs = load_songs(DATA_PATH)
    print(f"Loaded songs: {len(songs)}")

    adversarial_profiles = [
        {
            "label": "1. Contradictory Categorical + Continuous",
            "genre": "pop",
            "mood": "sad",
            "target_energy": 0.9,
            "target_acousticness": 0.2,
            "target_danceability": 0.85,
        },
        {
            "label": "2. Out-of-Range Target Values (Negative Score Bug)",
            "genre": "pop",
            "mood": "happy",
            "target_energy": 1.5,
            "target_acousticness": -0.2,
            "target_danceability": 0.85,
        },
        {
            "label": "3. Ghost Genre (No Categorical Bonus Ever)",
            "genre": "k-pop",
            "mood": "happy",
            "target_energy": 0.80,
            "target_acousticness": 0.20,
            "target_danceability": 0.85,
        },
        {
            "label": "4. Maximally Contradictory Continuous Features",
            "genre": "classical",
            "mood": "melancholic",
            "target_energy": 1.0,
            "target_acousticness": 1.0,
            "target_danceability": 1.0,
        },
        {
            "label": "5. Perfectly Centered Indecisive User",
            "genre": "lofi",
            "mood": "chill",
            "target_energy": 0.5,
            "target_acousticness": 0.5,
            "target_danceability": 0.5,
        },
        {
            "label": "6. Empty Genre and Mood",
            "genre": "",
            "mood": "",
            "target_energy": 0.80,
            "target_acousticness": 0.20,
            "target_danceability": 0.85,
        },
    ]

    divider = "─" * 50

    for user_prefs in adversarial_profiles:
        label = user_prefs.pop("label")
        recommendations = recommend_songs(user_prefs, songs, k=5)

        print(f"\n{divider}")
        print(f"  {label}")
        print(f"  Genre: '{user_prefs['genre']}'  |  Mood: '{user_prefs['mood']}'")
        print(f"  Energy: {user_prefs['target_energy']}  |  Acousticness: {user_prefs['target_acousticness']}  |  Danceability: {user_prefs['target_danceability']}")
        print(divider)

        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            print(f"\n  #{rank}  {song['title']} by {song['artist']}")
            print(f"       Score: {score:.2f}")
            print(f"       Why:")
            for reason in explanation.split(", "):
                print(f"         - {reason}")

        print()


if __name__ == "__main__":
    main()
