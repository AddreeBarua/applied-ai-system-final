# Model Card — VibeFinder 2.0

**Author:** Addree Barua  
**Course:** AI Engineering Program — Module 5 (Applied AI Systems)  
**Date:** April 2026  
**Base Project:** VibeFinder 1.0 (Module 3 — Music Recommender Simulation)

---

## 1. Model Name and Overview

**VibeFinder 2.0** is an AI-powered music recommender that extends VibeFinder 1.0 by adding Claude-generated natural-language explanations, retrieval-augmented generation (RAG), input guardrails, persistent logging, and an automated test harness.

---

## 2. Intended Use

VibeFinder 2.0 suggests 5 songs from a 20-song catalog based on a user's preferred genre, mood, energy level, and acoustic preference. The Claude API then generates a friendly, personalized explanation for each pick, grounded in song descriptions retrieved from a custom knowledge base.

**Intended for:**
- Course graders evaluating an applied AI system
- AI engineering students learning about RAG, guardrails, and LLM integration
- Portfolio reviewers on GitHub

**Not intended for:**
- Production music recommendation (catalog is too small)
- Decisions with real-world consequences
- Commercial deployment without additional safeguards

---

## 3. How It Works

VibeFinder 2.0 has two layers.

The first layer is the original scorer from VibeFinder 1.0: each song earns points for matching the user's preferred genre (+2.0), mood (+1.0), and energy level (0.0 to 1.0), with a small acoustic bonus (+0.5). The system sorts all 20 songs and picks the top 5.

The second layer generates explanations. Before calling the LLM, the system retrieves a one-sentence description of the song from a custom knowledge base (data/song_info.csv). It sends both the structured data and the retrieved description to Claude, which writes a friendly explanation grounded in those specifics. This is RAG — Retrieval-Augmented Generation. If Claude is unavailable, a template fallback runs automatically so the system never crashes.

Around all of this is a guardrail layer that validates and sanitizes each user profile before processing, and a logging layer that records every request and validation failure to logs/vibefinder.log.

---

## 4. Dataset

**data/songs.csv** — 20 songs with fields: id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, acousticness.

**data/song_info.csv** — New in VibeFinder 2.0. One hand-written sentence per song describing its sonic feel, instrumentation, and vibe, used as the RAG knowledge base.

Genres represented: pop, rock, lofi, hip-hop, edm, ambient, jazz, synthwave, indie pop, classical, country, rnb.

---

## 5. Limitations and Bias

- **Tiny catalog.** Only 20 songs exist. The system cannot recommend anything outside this set.
- **Genre dominates the score.** The +2.0 genre weight means a mediocre genre-matched song will always outscore a great non-genre-matched song.
- **Cultural bias in the knowledge base.** All 19 song descriptions were written by me, in English, reflecting my own listening background. Users from different cultural or musical backgrounds would describe these songs differently.
- **LLM non-determinism.** The same input can produce slightly different explanations on different runs. During testing, Claude once added an emoji that was not requested — a reminder that LLM output cannot be fully controlled by prompting alone.
- **No content filtering.** The system does not filter for explicit lyrics or themes. Additional safeguards would be required before deploying to general audiences.

---

## 6. Could Your AI Be Misused?

The main misuse risk is using AI-generated explanations to falsely promote songs a user would not actually enjoy — for example, a streaming platform generating glowing explanations to push songs that paid for placement, without disclosure.

To prevent this I would: (1) disclose clearly that explanations are AI-generated, (2) require explanations to be grounded in retrieved facts (which RAG already encourages), (3) log every explanation for auditing, and (4) never allow the LLM to override the rule-based scoring — Claude writes the explanation only, never decides the rank.

---

## 7. Evaluation and Testing Results

The system was evaluated three ways.

**Manual testing across 3 profiles.** I ran python -m src.main with three profiles (Happy Pop Fan, Chill Lofi Listener, Intense Rock Fan) and reviewed every result. Top-ranked songs matched the expected genre in all three cases. Explanations referenced specific song details drawn from the knowledge base in every run.

**Automated test harness.** tests/test_harness.py runs 6 tests covering 21 individual checks: 3 recommendation-quality tests (5 results returned, top genre matches expectation, top score above 3.0 threshold, AI explanation non-empty, explanation references song or artist name) and 3 guardrail-rejection tests (unknown genre, energy out of range, missing keys).

**Latest harness result: 6 out of 6 tests passed.**

**Pytest unit tests.** The original Module 3 unit tests in tests/test_recommender.py still pass after the upgrade.

**One-sentence summary:** 6/6 harness tests passed; all 3 valid profiles produced correctly-ranked results with grounded explanations, and all 3 invalid profiles were correctly rejected.

---

## 8. What Surprised Me During Testing

Two things surprised me. First, how much prompt wording changed output quality — adding "vary your openings" and "mention the song name" made Claude's explanations measurably more varied and specific. Second, how much the fallback layer earned its place. I tested it by removing my API key, and the system kept producing output with no errors or crashes. That confidence in graceful degradation is something I will now design into every AI project.

---

## 9. AI Collaboration During This Project

I used Claude (in chat) as a coding partner throughout this project for code generation, debugging, and design questions.

**Helpful suggestion:** When building src/guardrails.py, Claude suggested using dict.get(key, default) instead of direct dict[key] access when reading profile fields. I adopted this because it prevents KeyError if a field is missing and makes the validation layer more defensive. This pattern now appears throughout the file.

**Flawed suggestion:** Claude initially suggested using pip freeze > requirements.txt to capture dependencies. I ran the command and it dumped over 200 packages from my entire conda environment into the file — completely unusable for someone installing just my project. I rejected this and manually wrote a clean four-line requirements.txt listing only pytest, tabulate, anthropic, and python-dotenv. The lesson: a technically correct AI suggestion can be contextually wrong, and you need enough understanding to recognize that.

---

## 10. Future Improvements

- Replace the dictionary-based retriever with vector embeddings (sentence-transformers + FAISS) for semantic similarity search
- Expand the catalog to 200+ songs covering more genres and languages
- Add a user feedback loop (thumbs up/down) to re-rank results over time
- Build a Streamlit UI so users can edit profiles interactively
- Add prompt-caching to reduce API costs on repeated runs
- Add confidence scoring so Claude rates its own certainty on each explanation

---

## 11. Portfolio Reflection

This project taught me that an applied AI system is mostly plumbing around a model, not the model itself. About 80% of the code in this repo handles validation, retrieval, fallback, logging, and testing — and only one small function actually calls the LLM. That 80% is what separates a fragile demo from something you could ship. I will carry that lesson into every AI project I build.hese surrounding components are what make the system practical and trustworthy in real-world scenarios.