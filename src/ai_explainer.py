"""
AI Explainer Module — VibeFinder 2.0

This module uses Claude (Anthropic API) to generate natural-language 
explanations for why a song was recommended to a user.

NOW WITH RAG (Retrieval-Augmented Generation):
Before calling Claude, we retrieve a description of the song from our 
knowledge base (data/song_info.csv). This grounds Claude's explanation 
in real song-specific information instead of having it improvise.

Falls back to a simple template if the API is unavailable, so the 
system never breaks.
"""

import os
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables from .env file (where our API key lives)
load_dotenv()

# Import the RAG retriever (the R + A in RAG)
from src.rag_retriever import retrieve_song_info

# Try importing Anthropic SDK; we'll handle the case where it's missing
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


def generate_ai_explanation(
    song: Dict,
    user_profile: Dict,
    score: float,
    reasons: List[str]
) -> str:
    """
    Generate a natural-language explanation for why a song was recommended.
    
    Tries the Claude API first. If anything goes wrong (no key, network 
    error, rate limit), falls back to a clean template explanation.
    
    Args:
        song: Song dict with title, artist, genre, mood, energy, etc.
        user_profile: User's preferences (genre, mood, energy, likes_acoustic)
        score: The numeric score the song received
        reasons: List of reason strings from score_song()
    
    Returns:
        A friendly, conversational explanation string.
    """
    # Try the AI path first
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if ANTHROPIC_AVAILABLE and api_key:
        try:
            return _call_claude_api(song, user_profile, score, reasons, api_key)
        except Exception as e:
            # Log the error and fall back gracefully
            print(f"  [AI Explainer] API call failed ({type(e).__name__}), using fallback.")
            return _fallback_explanation(song, user_profile, reasons)
    else:
        # No API key or library — use fallback
        return _fallback_explanation(song, user_profile, reasons)


def _call_claude_api(
    song: Dict,
    user_profile: Dict,
    score: float,
    reasons: List[str],
    api_key: str
) -> str:
    """
    Make the actual API call to Claude and return its explanation.
    
    NOW WITH RAG: Retrieves song description from knowledge base 
    BEFORE building the prompt, so Claude can ground its explanation 
    in real song-specific information.
    
    Private helper — not meant to be called directly.
    """
    client = Anthropic(api_key=api_key)
    
    # 🔍 RAG STEP: Retrieve the song description from knowledge base
    song_description = retrieve_song_info(song.get('title', ''))
    
    # Build the "retrieved context" section of the prompt
    if song_description:
        retrieved_context = f"\nAdditional song context from our knowledge base:\n  {song_description}\n"
    else:
        retrieved_context = "\n(No additional song context available — use only the structured data above.)\n"
    
    # Build a clear, structured prompt for Claude
    prompt = f"""You are a friendly music recommendation assistant for VibeFinder, 
a music app that helps people discover songs they'll love.

A user has the following music taste:
- Favorite genre: {user_profile.get('genre', 'unknown')}
- Favorite mood: {user_profile.get('mood', 'unknown')}
- Preferred energy level: {user_profile.get('energy', 'unknown')} (0.0 = calm, 1.0 = intense)
- Likes acoustic music: {user_profile.get('likes_acoustic', False)}

Our recommender chose this song for them:
- Title: "{song.get('title', 'Unknown')}"
- Artist: {song.get('artist', 'Unknown')}
- Genre: {song.get('genre', 'unknown')}
- Mood: {song.get('mood', 'unknown')}
- Energy: {song.get('energy', 'unknown')}
{retrieved_context}
The match score is {score:.2f} out of 4.5.
The matching factors were: {', '.join(reasons) if reasons else 'no strong matches'}.

Write ONE conversational sentence (max 30 words) explaining why this song 
is a good pick for them. If the additional song context above is provided, 
USE IT — reference specific details from the description (instruments, mood, 
era, vibe) to make your explanation richer and more accurate. Be warm and 
specific. Mention the song or artist by name. Do not include the numeric score. 
Do not start with "This song" every time — vary your openings.
"""
    
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the text from the response
    explanation = response.content[0].text.strip()
    return explanation


def _fallback_explanation(
    song: Dict,
    user_profile: Dict,
    reasons: List[str]
) -> str:
    """
    Generates a clean template-based explanation when the API isn't available.
    Used as a graceful fallback so the system never crashes.
    
    Also tries to use the RAG knowledge base if available, even in fallback mode.
    """
    title = song.get('title', 'this song')
    artist = song.get('artist', 'the artist')
    
    # Even in fallback, try to use the knowledge base if available
    description = retrieve_song_info(title)
    
    if not reasons:
        if description:
            return f"{title} by {artist} — {description}"
        return f"{title} by {artist} is a gentle pick based on overall similarity."
    
    # Build a more readable sentence from the reasons
    matched_features = []
    if any("genre match" in r for r in reasons):
        matched_features.append(f"matches your love of {user_profile.get('genre', 'this genre')}")
    if any("mood match" in r for r in reasons):
        matched_features.append(f"fits your {user_profile.get('mood', 'preferred')} mood")
    if any("energy similarity" in r for r in reasons):
        matched_features.append("aligns with your energy preference")
    if any("acousticness bonus" in r for r in reasons):
        matched_features.append("has the acoustic feel you enjoy")
    
    if matched_features:
        base = f"{title} by {artist} {' and '.join(matched_features)}."
        if description:
            return f"{base} ({description})"
        return base
    else:
        return f"{title} by {artist} was the closest available match for your preferences."


# Quick self-test (only runs if you execute this file directly)
if __name__ == "__main__":
    test_song = {
        "title": "Sunrise City",
        "artist": "Neon Echo",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.82,
        "acousticness": 0.18
    }
    test_user = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False
    }
    test_reasons = ["genre match (+2.0)", "mood match (+1.0)", "energy similarity (+0.98)"]
    
    print("Testing AI Explainer with RAG...\n")
    explanation = generate_ai_explanation(test_song, test_user, 3.98, test_reasons)
    print(f"Generated explanation:\n  {explanation}\n")