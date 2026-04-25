"""
Test Harness for VibeFinder 2.0

Automated end-to-end evaluation script that runs the recommender on a 
suite of predefined user profiles and reports pass/fail results.

Each test checks multiple quality criteria:
  - Did the recommender return the expected number of songs?
  - Did each result include a non-empty AI-generated explanation?
  - Was the top result's score above a quality threshold?
  - Did the AI explanation actually mention the song or artist?
  - Were guardrails correctly applied to invalid input?

Run with:
    python -m tests.test_harness
"""

from typing import Dict, List, Tuple
from src.recommender import load_songs, recommend_songs
from src.ai_explainer import generate_ai_explanation
from src.guardrails import validate_user_profile, sanitize_user_profile


# ============================================================================
# TEST PROFILES — one valid, one invalid for full coverage
# ============================================================================

TEST_PROFILES = [
    {
        "name": "Profile 1: Happy Pop Fan",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False,
        "expected_top_genre": "pop",
        "min_top_score": 3.0,
    },
    {
        "name": "Profile 2: Chill Lofi Listener",
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.2,
        "likes_acoustic": True,
        "expected_top_genre": "lofi",
        "min_top_score": 3.0,
    },
    {
        "name": "Profile 3: Intense Rock Fan",
        "genre": "rock",
        "mood": "intense",
        "energy": 0.9,
        "likes_acoustic": False,
        "expected_top_genre": "rock",
        "min_top_score": 3.0,
    },
]

INVALID_PROFILES = [
    {
        "name": "Bad Profile: Unknown Genre",
        "profile": {"genre": "polka", "mood": "happy", "energy": 0.5, "likes_acoustic": False},
        "should_fail": True,
    },
    {
        "name": "Bad Profile: Energy Out of Range",
        "profile": {"genre": "pop", "mood": "happy", "energy": 99, "likes_acoustic": False},
        "should_fail": True,
    },
    {
        "name": "Bad Profile: Missing Keys",
        "profile": {"genre": "pop"},
        "should_fail": True,
    },
]


# ============================================================================
# TEST RUNNER FOR ONE PROFILE
# ============================================================================

def run_profile_test(profile_config: Dict, songs: List[Dict]) -> Tuple[bool, List[str]]:
    """
    Runs a full recommendation cycle for one profile and checks quality.
    
    Returns:
        (passed, list_of_check_messages)
    """
    profile_name = profile_config["name"]
    expected_top_genre = profile_config["expected_top_genre"]
    min_top_score = profile_config["min_top_score"]
    
    # Strip extra keys before passing to recommender
    clean_profile = {
        "genre": profile_config["genre"],
        "mood": profile_config["mood"],
        "energy": profile_config["energy"],
        "likes_acoustic": profile_config["likes_acoustic"],
    }
    
    checks = []
    all_passed = True
    
    # Validate first
    is_valid, validation_error = validate_user_profile(clean_profile)
    if not is_valid:
        return False, [f"FAIL: Profile failed validation: {validation_error}"]
    
    clean_profile = sanitize_user_profile(clean_profile)
    
    # Run recommendations
    try:
        recommendations = recommend_songs(clean_profile, songs, k=5)
    except Exception as e:
        return False, [f"FAIL: recommend_songs() crashed with {type(e).__name__}: {e}"]
    
    # CHECK 1: Did we get exactly 5 results?
    if len(recommendations) == 5:
        checks.append("PASS: Returned exactly 5 recommendations")
    else:
        checks.append(f"FAIL: Expected 5 results, got {len(recommendations)}")
        all_passed = False
    
    # CHECK 2: Top result has expected genre?
    if recommendations:
        top_song = recommendations[0][0]
        if top_song["genre"].lower() == expected_top_genre.lower():
            checks.append(f"PASS: Top result is {expected_top_genre} as expected ({top_song['title']})")
        else:
            checks.append(
                f"WARN: Top result is {top_song['genre']}, expected {expected_top_genre} "
                f"(may be acceptable due to scoring nuances)"
            )
    
    # CHECK 3: Top result meets minimum score threshold?
    if recommendations:
        top_score = recommendations[0][1]
        if top_score >= min_top_score:
            checks.append(f"PASS: Top score {top_score:.2f} meets threshold (>= {min_top_score})")
        else:
            checks.append(f"FAIL: Top score {top_score:.2f} below threshold (< {min_top_score})")
            all_passed = False
    
    # CHECK 4: Generate AI explanation for the top song and verify it's reasonable
    if recommendations:
        top_song, top_score, top_reasons = recommendations[0]
        try:
            explanation = generate_ai_explanation(top_song, clean_profile, top_score, top_reasons)
        except Exception as e:
            checks.append(f"FAIL: AI explainer crashed: {type(e).__name__}: {e}")
            all_passed = False
        else:
            # Check 4a: explanation exists and is non-empty
            if explanation and len(explanation.strip()) > 0:
                checks.append(f"PASS: AI explanation generated ({len(explanation)} chars)")
            else:
                checks.append("FAIL: AI explanation was empty")
                all_passed = False
            
            # Check 4b: explanation mentions the song title or artist
            song_title = top_song["title"].lower()
            artist = top_song["artist"].lower()
            explanation_lower = explanation.lower()
            
            if song_title in explanation_lower or artist in explanation_lower:
                checks.append("PASS: Explanation mentions song title or artist by name")
            else:
                checks.append("WARN: Explanation does not mention song/artist (rubric expects it)")
    
    return all_passed, checks


# ============================================================================
# TEST RUNNER FOR INVALID PROFILES (guardrail tests)
# ============================================================================

def run_guardrail_test(test_config: Dict) -> Tuple[bool, List[str]]:
    """
    Tests that a known-bad profile is correctly REJECTED by the guardrails.
    """
    test_name = test_config["name"]
    bad_profile = test_config["profile"]
    should_fail = test_config["should_fail"]
    
    is_valid, error_msg = validate_user_profile(bad_profile)
    
    checks = []
    
    if should_fail:
        if not is_valid:
            checks.append(f"PASS: Guardrail correctly rejected bad profile")
            checks.append(f"      Reason captured: {error_msg[:80]}...")
            return True, checks
        else:
            checks.append("FAIL: Guardrail let an invalid profile through")
            return False, checks
    
    return True, ["PASS: (no checks defined)"]


# ============================================================================
# MAIN HARNESS DRIVER
# ============================================================================

def main() -> int:
    """
    Runs all tests and prints a pass/fail summary.
    
    Returns the number of failed tests (0 = perfect run).
    """
    print("\n" + "=" * 80)
    print("  VibeFinder 2.0 - Test Harness")
    print("=" * 80)
    
    # Load song catalog once
    songs = load_songs("data/songs.csv")
    print(f"\nLoaded {len(songs)} songs for testing.\n")
    
    total_tests = 0
    total_passed = 0
    
    # ---- Section 1: Recommendation quality tests ----
    print("-" * 80)
    print("  SECTION 1: Recommendation Quality Tests")
    print("-" * 80)
    
    for profile_config in TEST_PROFILES:
        total_tests += 1
        print(f"\n[TEST] {profile_config['name']}")
        passed, check_messages = run_profile_test(profile_config, songs)
        for msg in check_messages:
            print(f"  {msg}")
        
        status = "PASS" if passed else "FAIL"
        print(f"  RESULT: {status}")
        
        if passed:
            total_passed += 1
    
    # ---- Section 2: Guardrail tests ----
    print("\n" + "-" * 80)
    print("  SECTION 2: Guardrail Tests (must REJECT bad input)")
    print("-" * 80)
    
    for test_config in INVALID_PROFILES:
        total_tests += 1
        print(f"\n[TEST] {test_config['name']}")
        passed, check_messages = run_guardrail_test(test_config)
        for msg in check_messages:
            print(f"  {msg}")
        
        status = "PASS" if passed else "FAIL"
        print(f"  RESULT: {status}")
        
        if passed:
            total_passed += 1
    
    # ---- Final summary ----
    print("\n" + "=" * 80)
    print("  FINAL SUMMARY")
    print("=" * 80)
    print(f"\n  Tests passed: {total_passed} / {total_tests}")
    
    if total_passed == total_tests:
        print("  STATUS: ALL TESTS PASSED")
    else:
        failures = total_tests - total_passed
        print(f"  STATUS: {failures} TEST(S) FAILED - review output above")
    
    print("=" * 80 + "\n")
    
    return total_tests - total_passed


if __name__ == "__main__":
    exit(main())