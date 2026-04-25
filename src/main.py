"""
Command line runner for the Music Recommender Simulation — VibeFinder 2.0

Now powered by Claude AI for natural-language recommendation explanations.
"""

from src.recommender import load_songs, recommend_songs
from src.ai_explainer import generate_ai_explanation
from tabulate import tabulate


def print_recommendations(profile_name: str, recommendations: list, user_profile: dict) -> None:
    """
    Displays recommendations in a formatted table with AI-generated explanations.
    
    Args:
        profile_name: Name of the user profile
        recommendations: List of tuples (song_dict, score, reasons_list)
        user_profile: User's preference dict (passed to AI explainer for context)
    """
    print(f"\n{'='*120}")
    print(f"  {profile_name}")
    print(f"{'='*120}")
    print(f"\n  🤖 Generating AI-powered explanations with Claude...\n")
    
    table_data = []
    
    for rank, rec in enumerate(recommendations, 1):
        song, score, reasons = rec
        
        # Call Claude to generate a natural-language explanation
        ai_explanation = generate_ai_explanation(
            song=song,
            user_profile=user_profile,
            score=score,
            reasons=reasons
        )
        
        table_data.append([
            rank,
            song['title'],
            song['artist'],
            song['genre'],
            song['mood'],
            f"{score:.2f}",
            ai_explanation
        ])
    
    headers = ["Rank", "Title", "Artist", "Genre", "Mood", "Score", "Why Recommended (AI-Generated)"]
    
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
    print()


def main() -> None:
    print("\n" + "="*120)
    print("  🎵 VibeFinder 2.0 — AI-Powered Music Recommender")
    print("="*120)
    
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
    
    profiles = [profile_1, profile_2, profile_3]
    
    for profile in profiles:
        profile_name = profile.pop("name")
        recommendations = recommend_songs(profile, songs, k=5)
        print_recommendations(profile_name, recommendations, profile)


if __name__ == "__main__":
    main()