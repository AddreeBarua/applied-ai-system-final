"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs
from tabulate import tabulate


def print_recommendations(profile_name: str, recommendations: list) -> None:
    """
    Displays recommendations in a formatted table.
    
    Args:
        profile_name: Name of the user profile
        recommendations: List of tuples (song_dict, score, explanation_string)
    """
    # Create table data
    table_data = []
    
    for rank, rec in enumerate(recommendations, 1):
        song, score, explanation = rec
        table_data.append([
            rank,
            song['title'],
            song['artist'],
            song['genre'],
            song['mood'],
            f"{score:.2f}",
            explanation
        ])
    
    # Define column headers
    headers = ["Rank", "Title", "Artist", "Genre", "Mood", "Score", "Why Recommended"]
    
    # Print profile header
    print(f"\n{'='*120}")
    print(f"  {profile_name}")
    print(f"{'='*120}\n")
    
    # Print formatted table
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    
    # Profile 1: Happy Pop Fan (High Energy)
    profile_1 = {
        "name": "Profile 1: Happy Pop Fan",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False
    }
    
    # Profile 2: Chill Lofi Listener (Low Energy)
    profile_2 = {
        "name": "Profile 2: Chill Lofi Listener",
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.2,
        "likes_acoustic": True
    }
    
    # Profile 3: Intense Rock Fan (Very High Energy)
    profile_3 = {
        "name": "Profile 3: Intense Rock Fan",
        "genre": "rock",
        "mood": "intense",
        "energy": 0.9,
        "likes_acoustic": False
    }
    
    # Test all three profiles
    profiles = [profile_1, profile_2, profile_3]
    
    for profile in profiles:
        profile_name = profile.pop("name")  # Extract name for display
        recommendations = recommend_songs(profile, songs, k=5)
        print_recommendations(profile_name, recommendations)


if __name__ == "__main__":
    main()
