# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeFinder 1.0** — A content-based music recommender that matches songs to your taste preferences.  

---

## 2. Intended Use  

VibeFinder is designed to show how content-based music recommendation works. It takes what you like (your favorite genre, mood, and energy level) and finds similar songs in the catalog that match your taste. This tool is built for learning and classroom exploration, not for real users with millions of songs—it's a simplified simulation to understand the fundamentals of how systems like Spotify recommend music.  

---

## 3. How the Model Works  

VibeFinder scores every song by comparing it to your preferences on four criteria. First, it gives 2 points if the genre matches (pop fan gets pop songs). Next, it adds 1 point if the mood matches (happy fan gets happy songs). Then it calculates how close the song's energy level is to yours on a 0-1 scale—songs with similar energy get up to 1 point. Finally, if you like acoustic music, songs with a lot of acoustic sound get a bonus 0.5 points. Once all songs are scored, it sorts them from highest to lowest and shows you the top 5 recommendations.  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

The model uses a dataset of 20 songs with attributes like genre, mood, energy level, tempo, and how acoustic they sound. The dataset includes 10 different genres (pop, lofi, rock, jazz, ambient, synthwave, indie pop, hip-hop, edm, classical, country, rnb) and diverse moods (happy, chill, intense, moody, relaxed, focused, energetic, romantic, sad, nostalgic, calm). This is a small, curated catalog built for learning, not a real music platform with millions of songs. Some modern music features like artist popularity or playlist co-occurrence are not included.  

---

## 5. Strengths  

The recommender works really well when users have clear, single preferences. For example, our "Happy Pop Fan" got "Sunrise City" as the top match, which perfectly captures what they like. The system also does a good job balancing multiple factors—it doesn't just match genre, but also considers mood and energy, so you get thoughtful recommendations instead of generic ones. The acousticness bonus helps acoustic-loving users get especially strong matches with songs like "Library Rain" that are both the right genre and have naturally acoustic sound.  

---

## 6. Limitations and Bias

The biggest issue is that genre dominates the scoring—it's worth 2 points while everything else is worth 1 or less. This means if a rock fan wants to discover pop music, they won't get good recommendations because non-rock songs start at a disadvantage. The dataset is also tiny (20 songs), so you're unlikely to find rare genres or niche moods. Most importantly, the system doesn't learn from your actual listening habits—it only looks at song features, not whether you actually liked past recommendations. In reality, music recommenders watch what you skip, replay, and add to playlists to get smarter over time.  

---

## 7. Evaluation  

I tested three different user profiles to see if the recommender behaved as expected. The "Happy Pop Fan" got "Sunrise City" with a score of 3.98—a perfect match with genre, mood, AND energy all aligned. The "Chill Lofi Listener" got "Library Rain" with 4.35 points, showing that the acousticness bonus really helps users who care about that feature. The "Intense Rock Fan" matched with "Storm Runner" at 3.99. All three results made intuitive sense and confirmed that the scoring logic works correctly. I looked for whether the top song matched the user's stated preferences, and in all three cases, it did.

---

## 8. Future Work  

To improve VibeFinder, I would rebalance the scoring so genre isn't so dominant—maybe make all factors worth 1-1.5 points instead of giving genre 2 points. I'd also add collaborative filtering so the system learns from what similar users liked, not just song features. Adding more songs and user testing would help find bugs and surprising cases. Finally, I'd explain recommendations in more detail by showing users exactly which song features matched their preferences, helping them understand why they got that recommendation.  

---

## 9. Personal Reflection  

Building VibeFinder taught me that recommender systems are harder than they look—balancing different factors (should genre or mood matter more?) involves real tradeoffs, and even small choices like scoring weights have big effects on what users see. I was surprised that the acousticness bonus made such a big difference for the lofi listener, showing that people care about different things. This project completely changed how I think about apps like Spotify: behind those "you might like this" recommendations is probably complex logic trying to balance showing you new things with showing you things similar to what you love. Simple systems like mine are the foundation, but real recommenders layer on so much more—your listening history, what your friends listen to, what's trending, and feedback loops that learn from your behavior.  
