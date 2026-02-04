# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Travel Agent AI for Goa (India) — a multi-agent travel planning system using hybrid vector search (Qdrant), LLM-based agents, real-time hotel verification (Tavily), and a Streamlit UI. The project is being **migrated from phidata to the datapizza-ai framework**.

## Key Files

- `travel_agent_base.py` — Original Colab notebook exported as Python. Contains the base implementation (data loading, embeddings, Qdrant setup, hybrid search, phidata agents). This is the starting point to refactor.
- `travel_agent_progetto.md` — Full project specification in Italian. Defines target architecture, agent personas, UI design, and all requirements.
- `datapizza-ai.txt` — Complete source dump of the datapizza-ai framework. Reference this for understanding the agent/tool/client APIs when migrating from phidata.

## Architecture

### Multi-Agent System (3 agents)
- **Hotel Agent (Marco)** — Hotel recommendations, uses `hotel_search_tool`. LLM: GPT-3.5-turbo.
- **Discovery Agent (Priya)** — Tourist attractions/places, uses `discover_places_tool`. LLM: GPT-3.5-turbo.
- **Planner Agent (Raj)** — Orchestrates the other two agents, builds day-by-day itineraries with geographic optimization and budget breakdown. LLM: GPT-4-turbo.

### Hybrid Search Pipeline
1. **Dense embeddings**: Sentence Transformers (`all-MiniLM-L6-v2`, 384 dims)
2. **Sparse embeddings**: TF-IDF (scikit-learn)
3. **Vector DB**: Qdrant with two collections (`goa_hotels`, `goa_places`), each storing both dense and sparse vectors
4. **Fusion**: Reciprocal Rank Fusion merging dense + sparse results
5. **Reranking**: Cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) on merged candidates

### Target Directory Structure (from spec)
```
goa_travel_agent/
├── config/settings.py
├── data/{raw,processed,cache}/
├── src/
│   ├── data_management/    # Kaggle download, CSV loading, preprocessing
│   ├── embeddings/         # HybridEmbedder, model manager, batch processing
│   ├── vector_db/          # Qdrant client wrapper, collection manager, searcher
│   ├── tools/              # hotel_search, places_search, tavily_verifier, itinerary_optimizer, budget_calculator
│   ├── agents/             # datapizza-ai agents (hotel, discovery, planner, orchestrator)
│   ├── utils/              # logger, cache, geo_utils, export
│   └── ui/                 # Streamlit app, components, pages, styles
└── tests/
```

## Critical Bug in Base Code

**TF-IDF is re-fitted per document** (`tfidf.fit([single_doc])` inside the loop). This produces incomparable sparse vectors since each has a different vocabulary. The fix: fit TF-IDF **once** on the entire corpus, then use only `tfidf.transform()` for individual documents. Save the fitted model with `joblib`.

## Required Environment Variables

```
OPENAI_API_KEY
QDRANT_URL
QDRANT_API_KEY
TAVILY_API_KEY
```

Kaggle credentials (`kaggle.json`) are also needed for dataset download.

## Data Sources

- Hotels: Kaggle dataset `PromptCloudHQ/hotels-on-goibibo` (filtered to state=Goa)
- Tourist places: Kaggle dataset `ritvik1909/indian-places-to-visit-reviews-data` (filtered to Goa cities)

## Framework Migration Notes

When migrating from phidata to datapizza-ai, map these concepts:
- `phi.agent.Agent` → datapizza-ai agent pattern (see `datapizza-ai.txt` for API)
- `phi.model.openai.OpenAIChat` → `datapizza.clients.openai.OpenAIClient`
- Tools remain plain Python functions with type hints and docstrings
- datapizza-ai supports multiple LLM clients: OpenAI, Anthropic, Google, Mistral, Bedrock, WatsonX

## Language

The project specification (`travel_agent_progetto.md`) and agent system prompts are in **Italian**. The codebase itself uses English for code and variable names.
