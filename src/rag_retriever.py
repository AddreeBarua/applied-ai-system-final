"""
RAG Retriever Module — VibeFinder 2.0

Loads a knowledge base of song descriptions from data/song_info.csv 
and provides a retrieval function that returns the description for 
a given song title.

This module is the "Retrieval" part of Retrieval-Augmented Generation (RAG):
the AI explainer calls retrieve_song_info() before generating an explanation, 
so Claude can ground its response in real song-specific information.
"""

import csv
from typing import Optional, Dict


# Module-level cache: load the knowledge base ONCE on import, 
# then look up from memory (avoids re-reading the CSV on every call)
_knowledge_base: Dict[str, str] = {}


def _load_knowledge_base(csv_path: str = "data/song_info.csv") -> None:
    """
    Loads song descriptions from the CSV into the in-memory dictionary.
    
    Called automatically on first lookup. Safe to call multiple times — 
    only reads the file once unless explicitly cleared.
    """
    global _knowledge_base
    
    if _knowledge_base:
        # Already loaded — skip
        return
    
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get("title", "").strip()
                description = row.get("description", "").strip()
                if title and description:
                    # Store with lowercase key for case-insensitive lookup
                    _knowledge_base[title.lower()] = description
        
        print(f"  [RAG] Loaded {len(_knowledge_base)} song descriptions into knowledge base.")
    
    except FileNotFoundError:
        print(f"  [RAG] Warning: Knowledge base not found at {csv_path}. Retrieval disabled.")
    except Exception as e:
        print(f"  [RAG] Error loading knowledge base: {e}")


def retrieve_song_info(song_title: str) -> Optional[str]:
    """
    Retrieves the description for a given song title.
    
    Args:
        song_title: The exact title of the song to look up
    
    Returns:
        The description string if found, or None if the song isn't 
        in the knowledge base (graceful fallback — caller should handle None)
    """
    # Lazy load on first call
    if not _knowledge_base:
        _load_knowledge_base()
    
    # Case-insensitive lookup
    return _knowledge_base.get(song_title.lower())


def knowledge_base_size() -> int:
    """
    Returns the number of songs currently in the knowledge base.
    Useful for diagnostics / logging.
    """
    if not _knowledge_base:
        _load_knowledge_base()
    return len(_knowledge_base)


# Quick self-test (only runs if you execute this file directly)
if __name__ == "__main__":
    print("\nTesting RAG Retriever...\n")
    
    # Test 1: Existing song
    info = retrieve_song_info("Storm Runner")
    print(f"Storm Runner → {info}")
    
    # Test 2: Different song
    info = retrieve_song_info("Library Rain")
    print(f"\nLibrary Rain → {info}")
    
    # Test 3: Case-insensitive lookup
    info = retrieve_song_info("sunrise CITY")
    print(f"\nsunrise CITY (mixed case) → {info}")
    
    # Test 4: Missing song (graceful fallback)
    info = retrieve_song_info("Imaginary Song That Doesn't Exist")
    print(f"\nMissing song → {info}")
    
    print(f"\nKnowledge base contains {knowledge_base_size()} songs total.\n")