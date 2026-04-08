"""
Scoring System for Content-Based Music Recommendation

Judges how well a song matches a user's taste profile.
"""


def score_song(song, user_prefs):
    """
    Calculate a recommendation score for a single song.
    
    Scoring Rules:
    - Genre match: +2.0 points (highest weight)
    - Mood match: +1.0 point
    - Energy similarity: 1.0 - abs(song_energy - user_energy)
    - Acousticness bonus: +0.5 if user likes acoustic and song > 0.6
    
    Args:
        song: Dictionary with keys: title, genre, mood, energy, acousticness
        user_prefs: Dictionary with keys: genre, mood, energy, likes_acoustic
    
    Returns:
        float: Total score (range: 0.0 to 4.5)
    """
    score = 0.0
    
    # Rule 1: Genre match (+2.0 points) - HIGHEST WEIGHT
    if song['genre'].lower() == user_prefs['genre'].lower():
        score += 2.0
    
    # Rule 2: Mood match (+1.0 point)
    if song['mood'].lower() == user_prefs['mood'].lower():
        score += 1.0
    
    # Rule 3: Energy similarity (0.0 to 1.0 points)
    # Songs with energy close to user preference get full 1.0 points
    # Songs with very different energy get close to 0.0 points
    energy_difference = abs(song['energy'] - user_prefs['energy'])
    energy_score = 1.0 - energy_difference  # Max difference is 1.0
    score += energy_score
    
    # Rule 4: Acousticness bonus (+0.5 points)
    # Only applies if user likes acoustic AND song is acoustic (> 0.6)
    if user_prefs.get('likes_acoustic', False):
        if song.get('acousticness', 0.0) > 0.6:
            score += 0.5
    
    return score


def explain_score(song, user_prefs):
    """
    Return detailed breakdown of why a song got its score.
    Useful for understanding recommendations.
    """
    breakdown = {}
    
    # Genre
    genre_match = song['genre'].lower() == user_prefs['genre'].lower()
    breakdown['genre'] = {
        'points': 2.0 if genre_match else 0.0,
        'reason': f"Genre {song['genre']} {'matches' if genre_match else 'does not match'} {user_prefs['genre']}"
    }
    
    # Mood
    mood_match = song['mood'].lower() == user_prefs['mood'].lower()
    breakdown['mood'] = {
        'points': 1.0 if mood_match else 0.0,
        'reason': f"Mood {song['mood']} {'matches' if mood_match else 'does not match'} {user_prefs['mood']}"
    }
    
    # Energy
    energy_diff = abs(song['energy'] - user_prefs['energy'])
    energy_score = 1.0 - energy_diff
    breakdown['energy'] = {
        'points': energy_score,
        'reason': f"Energy {song['energy']} vs user {user_prefs['energy']} (difference: {energy_diff:.2f})"
    }
    
    # Acousticness
    acoustic_bonus = 0.0
    acoustic_reason = "User does not prefer acoustic"
    if user_prefs.get('likes_acoustic', False):
        if song.get('acousticness', 0.0) > 0.6:
            acoustic_bonus = 0.5
            acoustic_reason = f"User likes acoustic, song has {song['acousticness']:.2f} acousticness"
        else:
            acoustic_reason = f"User likes acoustic, but song only has {song['acousticness']:.2f} acousticness"
    
    breakdown['acousticness'] = {
        'points': acoustic_bonus,
        'reason': acoustic_reason
    }
    
    total = sum(item['points'] for item in breakdown.values())
    breakdown['total'] = total
    
    return breakdown


# Example usage
if __name__ == "__main__":
    # Test with sample songs
    song1 = {'title': 'Sunrise City', 'genre': 'pop', 'mood': 'happy', 'energy': 0.82, 'acousticness': 0.18}
    song2 = {'title': 'Library Rain', 'genre': 'lofi', 'mood': 'chill', 'energy': 0.35, 'acousticness': 0.86}
    
    user = {'genre': 'pop', 'mood': 'happy', 'energy': 0.8, 'likes_acoustic': False}
    
    print("Testing Scoring System\n")
    print(f"User Profile: {user}\n")
    
    for song in [song1, song2]:
        score = score_song(song, user)
        breakdown = explain_score(song, user)
        
        print(f"Song: {song['title']}")
        print(f"Total Score: {score:.2f}/4.5")
        for key, value in breakdown.items():
            if key != 'total':
                print(f"  {key}: {value['points']:.2f}pts - {value['reason']}")
        print()
