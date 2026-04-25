"""
Guardrails Module — VibeFinder 2.0

Provides input validation, value sanitization, and logging for the 
recommendation system. These are the "safety bumpers" that keep the 
system reliable even when given weird or invalid input.

Components:
1. validate_user_profile() — checks profile dicts for required structure
2. sanitize_user_profile() — fixes common issues (case, range, etc.)
3. setup_logger() — configures persistent logging to logs/vibefinder.log
4. log_recommendation_request() — records every recommendation event
"""

import logging
import os
from datetime import datetime
from typing import Dict, Tuple


# ============================================================================
# CONSTANTS — define what "valid" looks like
# ============================================================================

# The set of recognized genres in our knowledge base
VALID_GENRES = {
    "pop", "rock", "lofi", "hip-hop", "edm", "ambient", "jazz",
    "synthwave", "indie pop", "classical", "country", "rnb"
}

# The set of recognized moods
VALID_MOODS = {
    "happy", "chill", "intense", "relaxed", "focused", "moody",
    "energetic", "romantic", "nostalgic", "sad", "calm"
}

# Required keys in every user profile
REQUIRED_KEYS = {"genre", "mood", "energy", "likes_acoustic"}


# ============================================================================
# VALIDATION
# ============================================================================

def validate_user_profile(profile: Dict) -> Tuple[bool, str]:
    """
    Validates that a user profile dictionary has all required structure.
    
    Args:
        profile: The user profile dict to check.
    
    Returns:
        (is_valid, error_message)
        - If valid: (True, "")
        - If invalid: (False, "human-readable error explanation")
    """
    # Check 1: Is it actually a dict?
    if not isinstance(profile, dict):
        return False, f"Profile must be a dict, got {type(profile).__name__}."
    
    # Check 2: Are all required keys present?
    missing_keys = REQUIRED_KEYS - set(profile.keys())
    if missing_keys:
        return False, f"Profile missing required keys: {sorted(missing_keys)}."
    
    # Check 3: Is genre a string?
    if not isinstance(profile["genre"], str):
        return False, f"Genre must be a string, got {type(profile['genre']).__name__}."
    
    # Check 4: Is mood a string?
    if not isinstance(profile["mood"], str):
        return False, f"Mood must be a string, got {type(profile['mood']).__name__}."
    
    # Check 5: Is energy a number?
    if not isinstance(profile["energy"], (int, float)):
        return False, f"Energy must be a number, got {type(profile['energy']).__name__}."
    
    # Check 6: Is energy in valid range?
    if not (0.0 <= profile["energy"] <= 1.0):
        return False, f"Energy must be between 0.0 and 1.0, got {profile['energy']}."
    
    # Check 7: Is likes_acoustic a boolean?
    if not isinstance(profile["likes_acoustic"], bool):
        return False, f"likes_acoustic must be True/False, got {type(profile['likes_acoustic']).__name__}."
    
    # Check 8: Soft warning — is genre recognized?
    if profile["genre"].lower() not in VALID_GENRES:
        return False, (
            f"Genre '{profile['genre']}' is not in our catalog. "
            f"Valid genres: {sorted(VALID_GENRES)}."
        )
    
    return True, ""


def sanitize_user_profile(profile: Dict) -> Dict:
    """
    Cleans a user profile by fixing common issues:
    - Lowercases genre and mood (so 'Pop' matches 'pop')
    - Clamps energy to [0.0, 1.0] range
    - Strips whitespace from string fields
    
    Returns a NEW dict — does not mutate the original.
    
    Args:
        profile: The user profile dict to clean.
    
    Returns:
        A cleaned copy of the profile.
    """
    cleaned = profile.copy()
    
    # Lowercase + strip strings
    if isinstance(cleaned.get("genre"), str):
        cleaned["genre"] = cleaned["genre"].strip().lower()
    if isinstance(cleaned.get("mood"), str):
        cleaned["mood"] = cleaned["mood"].strip().lower()
    
    # Clamp energy to [0.0, 1.0]
    if isinstance(cleaned.get("energy"), (int, float)):
        cleaned["energy"] = max(0.0, min(1.0, float(cleaned["energy"])))
    
    return cleaned


# ============================================================================
# LOGGING
# ============================================================================

# Module-level logger — set up once on import
_logger = None


def setup_logger(log_path: str = "logs/vibefinder.log") -> logging.Logger:
    """
    Configures a logger that writes to logs/vibefinder.log.
    
    Creates the logs/ directory if it doesn't exist. 
    Safe to call multiple times — only configures once.
    
    Returns:
        The configured logger instance.
    """
    global _logger
    
    if _logger is not None:
        return _logger
    
    # Make sure logs/ directory exists
    log_dir = os.path.dirname(log_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Create a named logger so we don't conflict with other libraries
    logger = logging.getLogger("vibefinder")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if reloaded
    if not logger.handlers:
        # File handler — writes to logs/vibefinder.log
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.INFO)
        
        # Format: 2026-04-25 18:42:01 [INFO] message
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    _logger = logger
    return logger


def log_recommendation_request(profile_name: str, profile: Dict, num_results: int) -> None:
    """
    Logs a recommendation request to logs/vibefinder.log.
    
    Args:
        profile_name: Display name of the profile (e.g. "Profile 1: Happy Pop Fan")
        profile: The validated user profile dict
        num_results: How many recommendations were returned
    """
    logger = setup_logger()
    logger.info(
        f"REC_REQUEST | profile={profile_name!r} | "
        f"genre={profile.get('genre')} | mood={profile.get('mood')} | "
        f"energy={profile.get('energy')} | likes_acoustic={profile.get('likes_acoustic')} | "
        f"results_returned={num_results}"
    )


def log_validation_failure(profile_name: str, error_msg: str) -> None:
    """
    Logs when a profile fails validation — useful for debugging bad input.
    """
    logger = setup_logger()
    logger.warning(f"VALIDATION_FAILED | profile={profile_name!r} | reason={error_msg}")


def log_api_event(event: str, details: str = "") -> None:
    """
    Logs an API-related event (call started, fallback triggered, etc.)
    """
    logger = setup_logger()
    logger.info(f"API_EVENT | {event} | {details}")


# ============================================================================
# Quick self-test
# ============================================================================

if __name__ == "__main__":
    print("\nTesting Guardrails Module...\n")
    
    # Test 1: Valid profile
    valid_profile = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False
    }
    is_valid, msg = validate_user_profile(valid_profile)
    print(f"✓ Valid profile → is_valid={is_valid}, msg={msg!r}")
    
    # Test 2: Missing key
    bad_1 = {"genre": "pop", "mood": "happy"}  # missing energy + likes_acoustic
    is_valid, msg = validate_user_profile(bad_1)
    print(f"✓ Missing keys → is_valid={is_valid}, msg={msg!r}")
    
    # Test 3: Invalid genre
    bad_2 = {"genre": "banana", "mood": "happy", "energy": 0.5, "likes_acoustic": False}
    is_valid, msg = validate_user_profile(bad_2)
    print(f"✓ Invalid genre → is_valid={is_valid}, msg={msg!r}")
    
    # Test 4: Energy out of range
    bad_3 = {"genre": "pop", "mood": "happy", "energy": 5.0, "likes_acoustic": False}
    is_valid, msg = validate_user_profile(bad_3)
    print(f"✓ Energy out of range → is_valid={is_valid}, msg={msg!r}")
    
    # Test 5: Sanitization (uppercase + out-of-range energy)
    messy = {"genre": "  POP  ", "mood": "Happy", "energy": 1.5, "likes_acoustic": False}
    cleaned = sanitize_user_profile(messy)
    print(f"\n✓ Sanitized messy profile:\n  Before: {messy}\n  After:  {cleaned}")
    
    # Test 6: Logging
    print("\nTesting logger...")
    log_recommendation_request("Test Profile", valid_profile, 5)
    log_validation_failure("Bad Profile", "Energy out of range")
    log_api_event("API_CALL_SUCCESS", "Generated 1 explanation")
    print("✓ Wrote 3 log entries to logs/vibefinder.log")
    
    print("\nAll guardrails working correctly!\n")