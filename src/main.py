"""
Command line runner for the Music Recommender Simulation - VibeFinder 2.0

Now powered by Claude AI for natural-language recommendation explanations,
with input validation, sanitization, and persistent logging via the
guardrails module.
"""

from src.recommender import load_songs, recommend_songs
from src.ai_explainer import generate_ai_explanation
from src.guardrails import (
    validate_user_profile,
    sanitize_user_profile,
    log_recommendation_request,
    log_validation_failure,
    setup_logger,
)
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
    print(f"\n  Generating AI-powered explanations with Claude...\n")

    table_data = []

    for rank, rec in enumerate(recommendations, 1):
        song, score, reasons = rec

        ai_explanation = generate_ai_explanation(
            song=song,
            user_profile=user_profile,
            score=score,
            reasons=reasons,
        )

        table_data.append([
            rank,
            song["title"],
            song["artist"],
            song["genre"],
            song["mood"],
            f"{score:.2f}",
            ai_explanation,
        ])

    headers = ["Rank", "Title", "Artist", "Genre", "Mood", "Score", "Why Recommended (AI-Generated)"]

    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
    print()


def process_profile(profile: dict, songs: list) -> None:
    """
    Validates, sanitizes, and runs recommendations for a single profile.
    Logs every step. Skips the profile gracefully if validation fails.
    """
    profile_name = profile.pop("name", "Unnamed Profile")

    # GUARDRAIL 1: Validate the profile structure and values
    is_valid, error_msg = validate_user_profile(profile)
    if not is_valid:
        print(f"\n[GUARDRAIL] Skipping '{profile_name}': {error_msg}\n")
        log_validation_failure(profile_name, error_msg)
        return

    # GUARDRAIL 2: Sanitize the profile (lowercase, clamp ranges)
    profile = sanitize_user_profile(profile)

    # Run the actual recommendation
    recommendations = recommend_songs(profile, songs, k=5)

    # GUARDRAIL 3: Log the request for auditing/debugging
    log_recommendation_request(profile_name, profile, len(recommendations))

    # Display the results
    print_recommendations(profile_name, recommendations, profile)


def main() -> None:
    # Initialize logger (creates logs/vibefinder.log if needed)
    setup_logger()

    print("\n" + "=" * 120)
    print("  VibeFinder 2.0 - AI-Powered Music Recommender")
    print("=" * 120)

    songs = load_songs("data/songs.csv")

    # Profile 1: Happy Pop Fan (High Energy)
    profile_1 = {
        "name": "Profile 1: Happy Pop Fan",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False,
    }

    # Profile 2: Chill Lofi Listener (Low Energy)
    profile_2 = {
        "name": "Profile 2: Chill Lofi Listener",
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.2,
        "likes_acoustic": True,
    }

    # Profile 3: Intense Rock Fan (Very High Energy)
    profile_3 = {
        "name": "Profile 3: Intense Rock Fan",
        "genre": "rock",
        "mood": "intense",
        "energy": 0.9,
        "likes_acoustic": False,
    }

    profiles = [profile_1, profile_2, profile_3]

    for profile in profiles:
        process_profile(profile, songs)


if __name__ == "__main__":
    main()