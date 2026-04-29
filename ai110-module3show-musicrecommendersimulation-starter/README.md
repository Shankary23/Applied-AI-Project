# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

  - For this recommender system we factor in these features from songs:
    - Genre
    - Mood
    - Energy
    - acousticness
    - danceability
  - The UserProfile will store the users energy and mood, to help make the system based on the users current needs.
  - The recommender computers a score by taking in the feature groups and assigning weights to each feature, then using Euclidean distance we can find the most similar songs.

  Weights table:

Feature group	  Type	        Points (max 10)
genre	          categorical	  3.0
mood	          categorical	  2.0
energy	        continuous	  2.0
danceability	  continuous	  1.5
acousticness	  continuous	  1.5


---

## Algorithm Recipe

  1. Load all songs from songs.csv into a list of dictionaries
  2. Read the user's taste profile (genre, mood, target energy, target danceability, target acousticness)
  3. For each song in the catalog:
     a. Award 3.0 pts if the song's genre exactly matches the user's preferred genre
     b. Award 2.0 pts if the song's mood exactly matches the user's preferred mood
     c. Compute energy score:      2.0 × (1 − |song.energy − target_energy|)
     d. Compute danceability score: 1.5 × (1 − |song.danceability − target_danceability|)
     e. Compute acousticness score: 1.5 × (1 − |song.acousticness − target_acousticness|)
     f. Sum all five values → total score (0–10)
     g. Record (song, score, explanation)
  4. Sort all scored songs from highest to lowest
  5. Return the top K results (default K = 5)

---

## Potential Biases

  - Genre dominance: with 3.0 pts, genre is the single biggest factor. A song that perfectly
    matches the user's mood, energy, and danceability but belongs to the wrong genre will almost
    always rank below a mediocre same-genre song. Great cross-genre discoveries get buried.

  - Mood is all-or-nothing: mood is scored as an exact match, so "relaxed" and "chill" are
    treated as completely different even though a listener might enjoy both. Near-synonyms get zero credit.

  - Catalog skew: the 19-song dataset has more lofi/indie/pop songs than metal, classical, or
    country. Users who prefer underrepresented genres will consistently receive lower top scores
    simply because fewer songs are available to match them.

  - No popularity or novelty signal: every song is treated equally regardless of how often it
    has been liked or how recently it was added, which may not reflect what a real listener wants.

---

## Sample Output

![Terminal output showing top 5 recommendations](Screenshot%202026-04-13%20at%209.24.11%20PM.png)

---

## Terminal Tests

Adversarial and edge-case profiles run against the recommender to probe scoring behavior.

**Profiles 1 & 2** — Contradictory Categorical + Continuous, and Out-of-Range Target Values:

![Terminal test output profiles 1 and 2](terminal_test/Screenshot%202026-04-13%20at%2010.13.02%20PM.png)

**Profile 3** — Ghost Genre (No Categorical Bonus Ever):

![Terminal test output profile 3](terminal_test/Screenshot%202026-04-13%20at%2010.13.10%20PM.png)

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

