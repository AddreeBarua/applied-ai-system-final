from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    
    Args:
        csv_path: Path to the CSV file containing song data
    
    Returns:
        List of dictionaries, each representing a song with columns:
        id, title, artist, genre, mood, energy, tempo_bpm, valence, 
        danceability, acousticness
    
    Converts to float: energy, tempo_bpm, valence, danceability, acousticness
    Prints total number of songs loaded.
    Required by src/main.py
    """
    songs = []
    
    # Columns to convert to float
    float_columns = ['energy', 'tempo_bpm', 'valence', 'danceability', 'acousticness']
    
    try:
        with open(csv_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Convert specified columns to float
                for col in float_columns:
                    if col in row:
                        row[col] = float(row[col])
                
                # Convert id to int
                if 'id' in row:
                    row['id'] = int(row['id'])
                
                songs.append(row)
        
        # Print confirmation with count
        print(f"Successfully loaded {len(songs)} songs from {csv_path}")
        return songs
    
    except FileNotFoundError:
        print(f"Error: File not found at {csv_path}")
        return []
    except ValueError as e:
        print(f"Error: Could not convert column to float: {e}")
        return []

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    
    Scoring Rules:
    - Genre match: +2.0 points
    - Mood match: +1.0 point
    - Energy similarity: 1.0 - abs(song_energy - user_energy), rounded to 2 decimals
    - Acousticness bonus: +0.5 if user likes acoustic and song acousticness > 0.6
    
    Args:
        user_prefs: Dict with keys "genre", "mood", "energy", "likes_acoustic"
        song: Dict with keys "genre", "mood", "energy", "acousticness"
    
    Returns:
        Tuple of (total_score, list_of_reasons)
    
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons = []
    
    # Rule 1: Genre match (+2.0)
    if song['genre'].lower() == user_prefs['genre'].lower():
        score += 2.0
        reasons.append("genre match (+2.0)")
    
    # Rule 2: Mood match (+1.0)
    if song['mood'].lower() == user_prefs['mood'].lower():
        score += 1.0
        reasons.append("mood match (+1.0)")
    
    # Rule 3: Energy similarity (0.0 to 1.0)
    energy_score = round(1.0 - abs(song['energy'] - user_prefs['energy']), 2)
    score += energy_score
    reasons.append(f"energy similarity (+{energy_score})")
    
    # Rule 4: Acousticness bonus (+0.5)
    if user_prefs.get('likes_acoustic', False):
        if song.get('acousticness', 0.0) > 0.6:
            score += 0.5
            reasons.append("acousticness bonus (+0.5)")
    
    return (score, reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    
    Scores all songs against user preferences, sorts by score (highest first),
    and returns the top k recommendations.
    
    Args:
        user_prefs: User preference dictionary with keys "genre", "mood", "energy", "likes_acoustic"
        songs: List of song dictionaries to score
        k: Number of top recommendations to return (default 5)
    
    Returns:
        List of tuples: (song_dict, score, explanation_string)
        where explanation_string is reasons joined by ", "
    
    Required by src/main.py
    """
    scored = []
    
    # Score each song
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons)
        scored.append((song, score, explanation))
    
    # Sort by score (highest to lowest)
    scored.sort(key=lambda x: x[1], reverse=True)
    
    # Return top k results
    return scored[:k]
