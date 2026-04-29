Ryan Shankar

- Original Project: Music recomender Simulation
    - The music recommenders goals were to goals were to:
        - Help identify songs that were similar to each other, to recommened similar song to the user
        - Create a realistic point system using different features as different weights prioritizing the ones that mattered most to the user, or in this case the creator, since we had some part in the decision of what features to prioriztize.
- The system diagram below, covers how the whole updated recommender works:
    - It takes user input, then places it in the RAG pipeline to get scores for the user's prefrences. Finally it outputs the top 5 songs and gives a reason.


- Setup Instructions:

### 1. Go to the project folder
```bash
cd ai110-module3show-musicrecommendersimulation-starter
```

### 2. Create and activate a virtual environment (first time only)
```bash
python3 -m venv .venv
source .venv/bin/activate
```
If you already have one, just activate it:
```bash
source .venv/bin/activate
```

### 3. Install dependencies (first time only)
```bash
pip install -r requirements.txt
```

### 4. Run the recommender
```bash
python src/main.py
```
This loads all 59 songs, runs 6 user profiles through the RAG pipeline, and prints the top 5 recommended songs for each with scores and explanations.

### 5. Run the tests
```bash
python -m pytest tests/ -v
```
You should see **10 passed** — 2 tests for the scorer and 8 tests for the retriever.






---

## Sample Interactions

### Example 1 — Clean match (lofi, chill, medium energy)

**Input:**
| Field | Value |
|---|---|
| Genre | lofi |
| Mood | chill |
| Energy | 0.5 |
| Danceability | 0.5 |
| Acousticness | 0.5 |

**Output (top 3):**
```
#1  Midnight Coding by LoRoom         Score: 9.19
      - genre matches (lofi): +1.5 pts
      - mood matches (chill): +1.5 pts
      - energy close match (0.42): +3.68 pts
      - danceability close match (0.62): +1.32 pts

#2  Afternoon Haze by Paper Lanterns  Score: 8.89
      - genre matches (lofi): +1.5 pts
      - mood matches (chill): +1.5 pts
      - energy close match (0.38): +3.52 pts
      - danceability close match (0.60): +1.35 pts

#3  Library Rain by Paper Lanterns    Score: 8.74
      - genre matches (lofi): +1.5 pts
      - mood matches (chill): +1.5 pts
      - danceability close match (0.58): +1.38 pts
```
> When genre and mood both match, scores are high (8–9+ range) and results are very focused.

---

### Example 2 — Mood mismatch (pop + sad, but high energy)

**Input:**
| Field | Value |
|---|---|
| Genre | pop |
| Mood | sad |
| Energy | 0.9 |
| Danceability | 0.85 |
| Acousticness | 0.2 |

**Output (top 3):**
```
#1  Golden Disco by Prism Era   Score: 8.12
      - genre matches (pop): +1.5 pts
      - energy close match (0.87): +3.88 pts
      - danceability close match (0.90): +1.42 pts
      - acousticness close match (0.08): +1.32 pts

#2  Gym Hero by Max Pulse       Score: 8.11
      - genre matches (pop): +1.5 pts
      - energy close match (0.93): +3.88 pts
      - danceability close match (0.88): +1.46 pts

#3  Sunrise City by Neon Echo   Score: 8.06
      - genre matches (pop): +1.5 pts
      - energy close match (0.82): +3.68 pts
      - danceability close match (0.79): +1.41 pts
```
> No songs in the catalog are "pop + sad", so the mood bonus never fires. The system falls back to genre and energy matches — showing the all-or-nothing mood bias documented in the model card.

---

### Example 3 — Ghost genre (k-pop not in catalog)

**Input:**
| Field | Value |
|---|---|
| Genre | k-pop |
| Mood | happy |
| Energy | 0.8 |
| Danceability | 0.85 |
| Acousticness | 0.2 |

**Output (top 3):**
```
#1  Pink Confetti by Sugarcoat      Score: 8.34
      - mood matches (happy): +1.5 pts
      - energy close match (0.79): +3.96 pts
      - danceability close match (0.85): +1.50 pts
      - acousticness close match (0.12): +1.38 pts

#2  Sunrise City by Neon Echo       Score: 8.30
      - mood matches (happy): +1.5 pts
      - energy close match (0.82): +3.92 pts
      - danceability close match (0.79): +1.41 pts
      - acousticness close match (0.18): +1.47 pts

#3  Rooftop Lights by Indigo Parade Score: 8.07
      - mood matches (happy): +1.5 pts
      - energy close match (0.76): +3.84 pts
      - danceability close match (0.82): +1.46 pts
```
> k-pop has zero songs in the catalog so the genre bonus never fires, but the system still returns strong results by matching on mood and continuous features. Scores are slightly lower (8.3 vs 9.2) because the 1.5 pt genre bonus is always missing.

---

## Design Decisions

### 1. Why RAG instead of scoring every song directly

The original system scored all songs in the catalog every time a user made a request. That works fine at 19 songs, but it doesn't scale — at 10,000 songs you'd be running the full weighted algorithm on every single entry. The RAG approach adds a cheap **retrieval step first**: convert each song and the user's query into a small set of tags, rank by tag overlap (Jaccard similarity), and only pass the top 15 candidates to the scorer.

**Trade-off:** The retrieval step could theoretically filter out a great song before it ever gets scored. For example, if a user asks for lofi but a jazz song happens to have the perfect energy and danceability, it might not make the candidate list. We accepted this trade-off because the retriever uses the same features the scorer uses, so a song with zero tag overlap is very unlikely to score well anyway.

---

### 2. Why Jaccard similarity for retrieval instead of vector embeddings

A more advanced retrieval step would convert songs into numeric vectors using a model like `sentence-transformers` and rank by cosine similarity. That would be more accurate but requires an external ML library, a model download, and significant compute for a 59-song catalog.

Jaccard similarity on hand-crafted tags (genre, mood, energy bucket, danceability bucket, acousticness bucket) is fast, transparent, and needs no dependencies beyond Python. You can read the tag sets and immediately understand why a song was retrieved.

**Trade-off:** Jaccard treats all tags as equally important and can't capture nuance (e.g., "relaxed" and "chill" have zero overlap even though they're similar moods). Embeddings would handle that, but at the cost of explainability and setup complexity.

---

### 3. Why exact match for genre and mood, but proximity scoring for energy/danceability/acousticness

Genre and mood are categorical — there's no meaningful middle ground between "rock" and "jazz". Giving partial credit for a wrong genre would make the results less predictable and harder to explain.

Energy, danceability, and acousticness are continuous values (0.0–1.0). A song with energy 0.79 when you asked for 0.8 is almost perfect — it shouldn't be punished the same as a song with energy 0.2. Using `1 - |delta|` gives smooth partial credit and rewards near-matches.

**Trade-off:** The all-or-nothing mood scoring is the biggest documented bias in the system. Two moods that feel nearly the same to a listener ("relaxed" and "chill") score identically to two moods that are completely opposite ("happy" and "sad").

---

### 4. Why energy has the highest weight (4.0 out of 10 pts)

The original weights gave genre the most influence (3.0 pts). After testing, genre dominance meant that a mediocre same-genre song almost always outranked a much better cross-genre song. Energy was raised to 4.0 because how hard or soft a song hits is the most immediate, moment-to-moment feeling a listener notices — more so than genre label.

**Trade-off:** Users who care deeply about genre over feel may find results surprising. This weight is a judgment call and could easily be tuned differently depending on the use case.

---

### 5. Why 59 songs instead of a real API

Pulling live data from the Spotify or Last.fm API would give a realistic catalog of millions of songs, but it adds authentication, rate limits, network dependency, and parsing complexity. A static CSV keeps the project self-contained, reproducible, and easy to grade.

**Trade-off:** The small catalog means some genres (e.g., k-pop, country) are underrepresented, which makes those user profiles consistently score lower — a known limitation documented in the model card.

---

# Music Recommender — System Diagram

```mermaid
flowchart TD
    U(["User Input\ngenre · mood · energy\ndanceability · acousticness"])
    CLI["CLI Entry Point\nsrc/main.py\nloads catalog, calls recommender"]
    CSV[("Database\ndata/songs.csv\n59 songs")]

    subgraph RAG ["RAG Pipeline"]
        R["RETRIEVE\nsrc/retriever.py\nJaccard tag similarity\n59 songs → 15 candidates"]
        S["SCORE\nsrc/recommender.py\nWeighted algorithm\n15 candidates → top 5"]
    end

    subgraph Eval ["Evaluator"]
        T1["Automated: pytest\ntest_retriever.py — 8 tests\ntest_recommender.py — 2 tests"]
        T2["Human: manual review\nRun app, inspect results,\nadjust weights or catalog"]
    end

    O(["Output\nTop 5 songs\nwith scores & explanations"])

    U --> CLI
    CLI --> R
    CSV --> R
    R -->|"15 candidates"| S
    S -->|"top 5"| O
    O --> T2
    T2 -->|"adjust weights"| S
    T2 -->|"add songs"| CSV

    T1 -. validates .-> R
    T1 -. validates .-> S
```

## Component key

| Component | File | Role |
|---|---|---|
| CLI Entry Point | `src/main.py` | Loads the catalog, defines user profiles, calls the recommender, and prints results |
| Database | `data/songs.csv` | 59 songs, each with genre, mood, energy, danceability, and acousticness |
| Retriever | `src/retriever.py` | RAG step 1 — tag-based Jaccard similarity narrows 59 songs to 15 candidates |
| Scorer | `src/recommender.py` | RAG step 2 — weighted algorithm ranks 15 candidates, returns top 5 with explanations |
| Automated Evaluator | `tests/` | pytest runs 10 tests that validate retriever correctness and scorer output |
| Human Evaluator | — | You run the app, read the printed results, and decide whether to adjust weights or add songs |
