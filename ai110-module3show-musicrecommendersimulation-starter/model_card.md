# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

    - Song Seeker

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate:
    - It gives recommendations based on users genre, mood, and how energetic they are feeling and how danceable the songs should be. It then generates the top 5 most similar songs to the users prefrences.
- What assumptions does it make about the user:
    - It assumes the users prefernces doesnt change and it doesnt have context or memory of the different profiles or users.
- Is this for real users or classroom exploration:
    - More for classroom exploration due to how much data is needed to train an accurate music recommender. While the concepts we learn cover most things its just the accuracy and data limits that stop us from being closer to a real product.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.):
    - It uses the genre to look for matches, then same for mood, then tries to match the energy level as much as possible, same with danceability and acousticness.

- What user preferences are considered:
    - The Genre, Mood, Target energy, Target danceability, and Target acousticness are considered.
- How does the model turn those into a score:  
    - It turns it into a score by assigning scores based on proximity. For example the mood and genre are scored based on if they match, so this is not graded on proximity. But for energy and the others, the closer the prospective values are the higher the score, these are all balanced out in the end to give a fully balanced score.
- What changes did you make from the starter logic:
    - I made sure the weights were different, this way I could try to make the recommender more built around what I thought would be useful. But logically nothing really changed other than that.

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog:
    - 19 songs in the dataset
- What genres or moods are represented:
    - Genres
        - lofi, pop, jazz, indie pop, rock, ambient, synthwave, folk, hip-hop, r&b, metal, country, electronic, classical
    - Moods
        - chill, intense, happy, relaxed, moody, energetic, focused, sad, romantic, melancholic, uplifting
- Did you add or remove data: 
    - Added data
- Are there parts of musical taste missing in the dataset
    - The tempo and varience are not used.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results:
    - Users who genre appears multiple times, the more similar entries they are the better the recommender system is since it has better matches.
- Any patterns you think your scoring captures correctly:
    - I think the scoring system correctly captures how continous features are scored. Since they use an adapting scale it can more accurately reflect what users actually want.
- Cases where the recommendations matched your intuition:
    - There were many cases where the recommender found the correct song and I was able to read the explanation to see why but on the mistakes it tried to justify very interesting and incorrect numbers just to achieve its goal.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider:
    - It does not consider valence and tempo_bpm.
- Genres or moods that are underrepresented:
    - Electronic, Metal, Hip-Hop, Lofi, all have one to three songs.
- Cases where the system overfits to one preference:
    - Energy outweighs, if a song has the right energy but doesnt have any other features it will get at least a 7. While if energy is off but other features are a match the max score is 5.
- Ways the scoring might unintentionally favor some users:
    - Some generes have more chances of matching while other genres only can have one or two matches.
    - Matching based on mood is done through string comparision so certain descriptions would get matched since even though they could be similar, since it uses the literal words to match.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested:
    - Pop/happy, Contradictory categorical + continuous (pop genre with sad mood ),Ghost genre (k-pop), Maximally contradictory continuous (classical/melancholic user requesting energy=1.0, acousticness=1.0, and danceability=1.0 simultaneously, which doesnt exist)
- What you looked for in the recommendations:
    - I looked for weather the top ranked songs in each profile made sense, like would a pop user want to listen to sad music, most likely not. So just going based on that, and just expanding that to other features.
- What surprised you:
    - One of the profiles tested negative which shouldnt be possible, and the fact that certain weights would lead to huge score gaps no matter what the user asked for which means the model was sensitive to contradiction.
- Any simple tests or comparisons you ran:
    - Manually calculting some of the scores, and also counting the songs per genre and mood to make sure everything was being covered accurately. 

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences:
    - Adding the features we did not use.
    - Letting users change their profile and see how the recommendations change.
- Better ways to explain recommendations:
    - Explaning why certain songs fit well while other songs dont, that way users aren't left wondering why this other song was not recommended. 

- Improving diversity among the top results:
    - Maybe adding categories or sub categories among those top results could help.
- Handling more complex user tastes:
    - Allowing different profiles will allow users to create multiple different accounts with different recommendations. 

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems:
    - I learned that they are far more complex than they seem.
- Something unexpected or interesting you discovered:
    - I learned a lot about the machine learning and how different practices can lead to different outcomes, but this exercise let me see directly why we use such complex formulas to calculate the weights and other features related to accuracy.
- How this changed the way you think about music recommendation apps:
    - Yes it makes sense why its not always accurate but considering everything they have to think about I think its fair.
