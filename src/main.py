"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


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
        
        print(f"\n{'='*60}")
        print(f"{profile_name}")
        print(f"{'='*60}")
        print(f"Genre: {profile['genre']} | Mood: {profile['mood']} | Energy: {profile['energy']} | Acoustic: {profile['likes_acoustic']}")
        print(f"\nTop 5 recommendations:\n")
        
        recommendations = recommend_songs(profile, songs, k=5)
        
        for rank, rec in enumerate(recommendations, 1):
            song, score, explanation = rec
            print(f"{rank}. {song['title']} - Score: {score:.2f}")
            print(f"   Because: {explanation}")
            print()


if __name__ == "__main__":
    main()
