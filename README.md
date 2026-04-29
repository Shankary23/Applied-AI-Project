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

## Testing Summary

### What we tested

The project has two layers of testing: **automated unit tests** (pytest) and **manual adversarial profiles** run through the CLI.

**Automated tests — 10 total, all passing**

| Test file | Tests | What they check |
|---|---|---|
| `test_retriever.py` | 8 | Candidate count, catalog-size cap, genre surfacing, Jaccard ordering, empty genre edge case, Jaccard math (perfect/zero/empty overlap) |
| `test_recommender.py` | 2 | Top result matches expected genre/mood, explanation string is non-empty |

**Adversarial CLI profiles — 6 hand-crafted edge cases**

| Profile | What it probes |
|---|---|
| Contradictory categorical + continuous | Genre matches but mood doesn't — does energy still dominate? |
| Out-of-range target values | Energy 1.5 and acousticness −0.2 — does the math break? |
| Ghost genre (k-pop) | Genre not in catalog — does the system crash or degrade gracefully? |
| Maximally contradictory continuous | Classical/melancholic user asking for energy 1.0 and danceability 1.0 |
| Perfectly centered user | All targets at 0.5 — does the system pick something reasonable? |
| Empty genre and mood | Blank strings — does anything crash? |

---

### What worked

- **All 10 automated tests pass** with no failures or warnings.
- **Empty and missing genre/mood strings** are handled gracefully — the retriever skips them and falls back to matching on continuous feature buckets only.
- **Ghost genre** (k-pop, which has no songs in the catalog) does not crash the system. It simply never awards the genre bonus and still returns 5 relevant results based on mood and energy.
- **The RAG retrieval step** consistently surfaces the right genre cluster at the top of the candidate list, which means the scorer only has to break ties — not search the whole catalog.
- **Proximity scoring** for continuous features (energy, danceability, acousticness) worked well — near-matches get meaningful partial credit rather than being penalized the same as poor matches.

---

### What didn't work

- **Out-of-range inputs produce negative score contributions.** When a user sets energy to 1.5 or acousticness to −0.2, the formula `1 - |delta|` returns a negative number, dragging the total score down. The system doesn't crash, but the scores are misleading. A clamping fix (`max(0, ...)`) would prevent this.
- **Mood is all-or-nothing.** In the contradictory profile (pop + sad), no pop songs in the catalog are tagged "sad", so the mood bonus never fires. The system falls back entirely to genre and energy. Two moods that feel similar to a listener ("relaxed" vs "chill") score the same as two opposite moods.
- **Small catalog limits underrepresented genres.** Users asking for k-pop, country, or classical always get lower top scores because fewer songs exist to match them — not because those preferences are hard to satisfy.
- **No cross-genre discovery.** Because genre is still worth 1.5 pts on an exact match, a perfect-energy song in the wrong genre almost always ranks below an average song in the right genre.

---

### What I learned

- **Testing edge cases revealed real bugs.** The out-of-range score bug was only visible because an adversarial profile deliberately pushed energy to 1.5 — a normal user test would never catch it.
- **The retrieval step changes what gets scored, not just how fast.** By filtering to 15 candidates first, the RAG pipeline means some songs never reach the scorer at all. This made us more careful about what the retriever prioritizes.
- **Weights are the hardest part to get right.** Changing energy from 2.0 to 4.0 pts noticeably shifted results away from genre-dominant picks. Small weight changes have outsized effects on which song lands at #1 vs #5, and there is no objectively "correct" answer — it depends on what the user actually values.
- **Transparency helps evaluation.** Because every result prints a per-criterion breakdown ("genre matches: +1.5 pts"), it was easy to see exactly why the system made each choice and where the scoring logic was falling short.

---



### 1. Why RAG instead of scoring every song directly

The original system scored all songs in the catalog every time a user made a request. That works fine at 19 songs, but it doesn't scale — at 10,000 songs you'd be running the full weighted algorithm on every single entry. The RAG approach adds a cheap **retrieval step first**: convert each song and the user's query into a small set of tags, rank by tag overlap (Jaccard similarity), and only pass the top 15 candidates to the scorer.

**Trade-off:** The retrieval step could theoretically filter out a great song before it ever gets scored. For example, if a user asks for lofi but a jazz song happens to have the perfect energy and danceability, it might not make the candidate list. I accepted this trade-off because the retriever uses the same features the scorer uses, so a song with zero tag overlap is very unlikely to score well anyway.

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

## Reliability & Testing Summary

- **Automated tests:** 10 unit tests across `test_retriever.py` (8 tests) and `test_recommender.py` (2 tests) — all passing. Tests cover candidate count, genre surfacing, Jaccard ordering, edge cases (empty genre, out-of-range inputs), and scorer output.
- **Confidence scoring:** every result prints a score out of 10 with a label — `[HIGH confidence]` (8.0+), `[MEDIUM confidence]` (6.0–7.9), or `[LOW confidence]` (below 6.0) — so you can immediately see how well the system matched the request.
- **Human evaluation:** 6 adversarial profiles were run manually through the CLI to probe edge cases (ghost genre, out-of-range values, empty strings, contradictory inputs). Results were inspected by hand to verify the system behaved as expected.
- **Error handling:** empty genre/mood strings and out-of-range values (e.g. energy = 1.5) do not crash the system — results still return, and the confidence label will show `LOW` when the match is poor.

## AI Reflection

Some limitations in our system is the fact that it is local.

**What are the limitations or biases in your system?**

The biggest limitation is that this is a rule-based RAG system — it can match patterns, but it cannot make complex decisions. It doesn't understand that "relaxed" and "chill" mean nearly the same thing, or that a jazz song might feel right to someone who asked for lofi. Every decision comes down to tag overlap and weighted math, so it can only be as good as the data and rules we give it. The clearest bias is genre dominance — even after lowering the genre weight, a mediocre song in the right genre often still beats a great song in the wrong genre. There is also a catalog skew bias: genres like k-pop, classical, and country have far fewer songs than lofi or pop, so users with those preferences consistently get lower confidence scores — not because the system failed, but because there simply weren't enough matching songs to choose from.

**Could your AI be misused, and how would you prevent that?**

This system is unlikely to cause serious harm — it recommends songs, not medical advice or financial decisions. The most realistic misuse would be trusting a `[HIGH confidence]` label on a result that doesn't actually match what the user wanted, because the score is based on our weights, not real user satisfaction. Someone could take that label at face value and trust it more than they should. The fix is improving the underlying scoring: better weights, a larger catalog, and fuzzy mood matching so near-synonyms get partial credit. Adding user feedback — letting the listener rate results — would also help catch cases where the system is confidently wrong.

**What surprised you while testing your AI's reliability?**

The most surprising thing was how often the AI I was using to build this system would suggest something that would make the code less reliable — and then catch itself and acknowledge it. For example, it would propose a feature, note that it could produce negative scores with out-of-range inputs, and then either fix it or flag it as a known issue. That back-and-forth made me realize that AI tools are not just "correct or wrong" — they reason through trade-offs in real time, and the reasoning is just as important as the output. It changed how I think about reliability: it's not about never making mistakes, it's about catching them and being transparent about what the system can and can't do.


### Reflection: 
- This project taught me about how powerful AI as a tool can be. I tried not to rely on AI too much, but this course has shown me that if we know the decisions and ideas before prompting we can understand the outputs of the AI models better and further improve our code and project. It is a very effective tool when used as we did in this course. I also learned that it is not perfect. Many of our projects became complex and whether it was due to hallucinations or context windows, the AI models suggestions would be more deterimental than helpful. So blindly relying on it could take you further away from the goal that towards it. Overall it was a great and informative experience, and I learned many things about AI, both concepts and how to better utilize models themselves.