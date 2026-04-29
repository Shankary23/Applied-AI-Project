# Model Card: Music Recommender Simulation

## 1. Model Name

Song Seeker 2.0 — updated with RAG pipeline

---

## 2. Intended Use

- What kind of recommendations does it generate:
    - It gives recommendations based on users genre, mood, and how energetic they are feeling and how danceable the songs should be. It then generates the top 5 most similar songs to the users prefrences.
- What assumptions does it make about the user:
    - It assumes the users prefernces doesnt change and it doesnt have context or memory of the different profiles or users.
- Is this for real users or classroom exploration:
    - More for classroom exploration due to how much data is needed to train an accurate music recommender. While the concepts we learn cover most things its just the accuracy and data limits that stop us from being closer to a real product.

---

## 3. How the Model Works

The updated system uses a two-step RAG (Retrieval-Augmented Generation) pipeline instead of scoring every song directly.

**Step 1 — Retrieve:** Before any scoring happens, the system converts each song into a set of tags (genre, mood, and buckets for energy, danceability, and acousticness). The user's preferences are converted into the same tag format. Songs are then ranked by Jaccard similarity — how much their tags overlap with the user's query — and the top 15 candidates are selected. This narrows the catalog before the more expensive scoring step runs.

**Step 2 — Score:** The weighted scoring algorithm runs only on those 15 candidates.

- What features of each song are used:
    - It uses the genre to look for matches, then same for mood, then tries to match the energy level as much as possible, same with danceability and acousticness.
- What user preferences are considered:
    - The Genre, Mood, Target energy, Target danceability, and Target acousticness are considered.
- How does the model turn those into a score:
    - It turns it into a score by assigning scores based on proximity. For example the mood and genre are scored based on if they match, so this is not graded on proximity. But for energy and the others, the closer the prospective values are the higher the score, these are all balanced out in the end to give a fully balanced score.
- What changes did you make from the starter logic:
    - I made sure the weights were different, this way I could try to make the recommender more built around what I thought would be useful. But logically nothing really changed other than that. The major addition is the retrieval step, which filters the catalog down to 15 candidates before scoring runs, following the RAG pattern.

**Confidence labels:** Every result now prints a confidence label alongside its score — HIGH (8.0+), MEDIUM (6.0–7.9), or LOW (below 6.0 out of 10) — so the output is transparent about how well the system matched the request.

---

## 4. Data

- How many songs are in the catalog:
    - 59 songs (expanded from the original 19 to make the retrieval step meaningful)
- What genres or moods are represented:
    - Genres: lofi, pop, jazz, indie pop, rock, ambient, synthwave, folk, hip-hop, r&b, metal, country, electronic, classical
    - Moods: chill, intense, happy, relaxed, moody, energetic, focused, sad, romantic, melancholic, uplifting
- Did you add or remove data:
    - Added data — 40 new songs were added across all existing genres to bring the total to 59. This was necessary so the retrieval step has enough songs to meaningfully filter.
- Are there parts of musical taste missing in the dataset:
    - The tempo and varience are not used.

---

## 5. Strengths

- User types for which it gives reasonable results:
    - Users who genre appears multiple times, the more similar entries they are the better the recommender system is since it has better matches.
- Any patterns you think your scoring captures correctly:
    - I think the scoring system correctly captures how continous features are scored. Since they use an adapting scale it can more accurately reflect what users actually want.
- Cases where the recommendations matched your intuition:
    - There were many cases where the recommender found the correct song and I was able to read the explanation to see why but on the mistakes it tried to justify very interesting and incorrect numbers just to achieve its goal.
- New strength from the RAG update: The retrieval step consistently surfaces the correct genre cluster before scoring even runs, which means the scorer only has to break ties rather than search the whole catalog.

---

## 6. Limitations and Bias

- Features it does not consider:
    - It does not consider valence and tempo_bpm.
- Genres or moods that are underrepresented:
    - Electronic, Metal, Hip-Hop, Lofi, all have one to three songs.
- Cases where the system overfits to one preference:
    - Energy outweighs, if a song has the right energy but doesnt have any other features it will get at least a 7. While if energy is off but other features are a match the max score is 5.
- Ways the scoring might unintentionally favor some users:
    - Some generes have more chances of matching while other genres only can have one or two matches.
    - Matching based on mood is done through string comparision so certain descriptions would get matched since even though they could be similar, since it uses the literal words to match.
- New limitation from the RAG update: The retrieval step could theoretically filter out a good song before it reaches the scorer. If a song has the perfect energy and danceability but belongs to a genre the user didn't ask for, it might not make the candidate list at all.

---

## 7. Evaluation

- Which user profiles you tested:
    - Pop/happy, Contradictory categorical + continuous (pop genre with sad mood), Ghost genre (k-pop), Maximally contradictory continuous (classical/melancholic user requesting energy=1.0, acousticness=1.0, and danceability=1.0 simultaneously, which doesnt exist)
- What you looked for in the recommendations:
    - I looked for weather the top ranked songs in each profile made sense, like would a pop user want to listen to sad music, most likely not. So just going based on that, and just expanding that to other features.
- What surprised you:
    - One of the profiles tested negative which shouldnt be possible, and the fact that certain weights would lead to huge score gaps no matter what the user asked for which means the model was sensitive to contradiction.
- Any simple tests or comparisons you ran:
    - Manually calculting some of the scores, and also counting the songs per genre and mood to make sure everything was being covered accurately.
- Automated testing added in v2.0:
    - 10 unit tests added across two files. `test_retriever.py` (8 tests) checks candidate count, genre surfacing, Jaccard ordering, and edge cases like empty genre strings and Jaccard math. `test_recommender.py` (2 tests) checks that the top result matches expected genre/mood and that explanations are non-empty. All 10 pass.

---

## 8. Future Work

- Additional features or preferences:
    - Adding the features we did not use.
    - Letting users change their profile and see how the recommendations change.
- Better ways to explain recommendations:
    - Explaning why certain songs fit well while other songs dont, that way users aren't left wondering why this other song was not recommended.
- Improving diversity among the top results:
    - Maybe adding categories or sub categories among those top results could help.
- Handling more complex user tastes:
    - Allowing different profiles will allow users to create multiple different accounts with different recommendations.
- RAG improvements:
    - Replacing the tag-based Jaccard retrieval with vector embeddings would allow the system to understand that "relaxed" and "chill" are similar moods, which the current system cannot do.

---

## 9. Personal Reflection

- What you learned about recommender systems:
    - I learned that they are far more complex than they seem.
- Something unexpected or interesting you discovered:
    - I learned a lot about the machine learning and how different practices can lead to different outcomes, but this exercise let me see directly why we use such complex formulas to calculate the weights and other features related to accuracy.
- How this changed the way you think about music recommendation apps:
    - Yes it makes sense why its not always accurate but considering everything they have to think about I think its fair.
