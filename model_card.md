# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

MUSE 1.0
I wanted something that felt a bit more personal and “curated,” like it’s picking music that fits a mood or aesthetic rather than just doing strict filtering.

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  
This system is meant to recommend a small set of songs from a limited catalog based on a user’s preferences like genre, mood, energy, and whether they like acoustic sounds. It’s mainly for classroom exploration, so the goal is to understand how recommendation systems work and how design choices like weighting and scoring affect results. It is not meant for real-world deployment, but more for learning how user preferences can be turned into ranked outputs.
---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.
My model works by comparing each song to the user’s preferences across multiple features and then turning that comparison into a single score. It looks at song features like genre, mood, energy, valence, danceability, and acousticness. Genre and mood are treated as the strongest signals because they represent the overall identity and vibe of the song, while the numeric features capture more detailed aspects of how the song actually feels.

On the user side, the system uses their favorite genre, favorite mood, target energy level, and whether they prefer acoustic or non-acoustic music. The model assigns points when features match (like genre or mood) and also gives partial credit based on how close numeric values are to the user’s preferences, especially for energy and acousticness. All of these contributions are combined into one final score, and songs are ranked by that score. Compared to the starter version, I made the scoring more balanced across multiple features so it doesn’t rely too heavily on just one signal like genre, and instead reflects a more complete view of user preference.
---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  
The dataset contains 10 songs stored in data/songs.csv, with a mix of genres like pop, lofi, rock, jazz, ambient, synthwave, and indie pop. It also includes moods such as happy, chill, intense, relaxed, and focused, along with numeric audio features like energy, tempo, valence, danceability, and acousticness. I did not modify the dataset, but it is very small and not fully representative of real music platforms. Most of the songs reflect a simple “vibe-based” collection, so it’s more like a curated sample for testing logic rather than a realistic or balanced music library.
---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  
My system works really well when the user has clear and consistent preferences, like when someone is looking for upbeat pop with high energy or chill lofi with low energy. In those cases, the top results usually feel very accurate because the scoring system reinforces matching signals across multiple features. It’s also strong in terms of transparency since I can clearly explain why each song was recommended, which makes it easy to understand and debug compared to more complex black-box recommenders.
---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  
One major limitation is that the system is heavily affected by the small size of the dataset, so recommendations can reflect what is available rather than true user intent. It also has a bias toward genre matching since genre is weighted strongly, which can create a loop where users keep seeing similar types of songs and don’t get much discovery. On top of that, it doesn’t fully handle conflicting preferences well, like when a user wants high energy but also a mellow mood, which can lead to odd or unbalanced recommendations.
---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.
I tested the recommender by creating multiple user profiles and checking whether the top recommended songs matched what I would expect based on their preferences. For simple profiles with clear taste (like pop + upbeat + high energy), the results were consistently good and aligned with intuition. For more mixed profiles, I looked at whether the system balanced different features or over-prioritized one signal like genre or energy. I also compared results across different genres to see if any type of user was consistently underserved or if certain features were dominating the ranking.
---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  
If I had more time, I would improve the system by adding more features like tempo ranges and lyric themes so the recommendations feel more complete and not just based on audio vibes. I would also work on improving diversity so the system doesn’t over-focus on one genre and instead includes more variety in the top results. Another improvement would be better handling of conflicting preferences so the model can understand tradeoffs instead of just averaging everything together.
---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
This project helped me understand how recommender systems are really just structured ways of turning human preferences into numbers and then ranking based on those values. I realized that even small design choices like weighting genre more heavily can completely change the output and create bias without it being obvious at first. It also made me see how real systems like Spotify probably have to deal with way more complexity around fairness, diversity, and explainability, not just accuracy.