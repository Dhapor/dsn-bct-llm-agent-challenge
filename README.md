# DSN x BCT LLM Agent Challenge Submission

**Data and AI Summit Hackathon 3.0**

Two AI agents that model how Nigerian users behave online and recommend things they would actually enjoy. Built with FastAPI, FAISS vector search, and the Claude API as the reasoning backbone.

---

## Live Agents

| Agent | Interactive Docs | Quick Test |
|---|---|---|
| Task A — User Modeling | [/docs](https://dsn-bct-task-a-v9ik.onrender.com/docs) | [/test](https://dsn-bct-task-a-v9ik.onrender.com/test) |
| Task B — Recommendation | [/docs](https://dsn-bct-task-b-11lm.onrender.com/docs) | [/catalog](https://dsn-bct-task-b-11lm.onrender.com/catalog) |

> **Note:** Services are on Render's free tier and may take 30–60 seconds to wake up on first request.

### Quickest way to see them working

- **Task A:** open `https://dsn-bct-task-a-v9ik.onrender.com/test` in your browser — returns a real Claude-generated review instantly, no setup needed.
- **Task B:** open `https://dsn-bct-task-b-11lm.onrender.com/docs`, click **POST /recommend → Try it out**, paste the example payload, click Execute.

---

## What I Built

**Task A** takes a user's review history and generates a review they would likely write for a new item, including the star rating. The goal was not just to predict a number but to capture how that specific person writes, what they notice, and how they express it.

**Task B** takes a user profile and returns a ranked list of personalised recommendations. Instead of simple collaborative filtering, I built an agentic workflow where the system searches, evaluates candidates, and reasons about fit before committing to a final list.

Both agents are containerised and can be started with one command.

---

## Project Structure

```
project/
├── task_a/
│   ├── agents/
│   │   └── review_generator.py
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── task_b/
│   ├── agents/
│   │   └── recommender_agent.py
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── shared/
│   ├── user_profiler.py
│   ├── nigerian_adapter.py
│   ├── vector_store.py
│   └── sample_catalog.py
├── docker-compose.yml
└── solution_paper/
    └── solution_paper.md
```

---

## Running It

### With Docker (recommended)

```bash
git clone https://github.com/Dhapor/dsn-bct-llm-agent-challenge
cd dsn-bct-llm-agent-challenge

cp .env.example .env
# Add your ANTHROPIC_API_KEY to the .env file

docker-compose up --build
```

Task A runs on port 8001, Task B on port 8002.

### Without Docker

```bash
pip install -r task_a/requirements.txt
pip install -r task_b/requirements.txt

export ANTHROPIC_API_KEY=your_key_here

cd task_a && PYTHONPATH=.. uvicorn main:app --port 8001
cd task_b && PYTHONPATH=.. uvicorn main:app --port 8002
```

---

## API Endpoints

### Task A: POST /generate-review

Input is a user persona with their review history plus the details of the item they are reviewing.

```bash
curl -X POST http://localhost:8001/generate-review \
  -H "Content-Type: application/json" \
  -d '{
    "user_persona": {
      "user_id": "u_chidi",
      "name": "Chidi",
      "location": "Lagos, Nigeria",
      "preferences": ["spicy food", "value for money"],
      "review_history": [
        {
          "item": "Yellow Chilli",
          "rating": 4.5,
          "review": "E sweet me die! The oxtail pepper soup na the best in Lagos.",
          "category": "restaurant"
        }
      ]
    },
    "product_details": {
      "name": "Kilimanjaro Restaurant",
      "category": "restaurant",
      "cuisine": "Nigerian",
      "description": "Grills and suya in Lekki",
      "price_range": "$$"
    }
  }'
```

Output:
```json
{
  "rating": 4.0,
  "review": "Their suya na fire! Lekki location convenient. Price fair for the quality.",
  "reasoning": "User averages 4.0 for mid-range Nigerian spots..."
}
```

### Task B: POST /recommend

```bash
curl -X POST http://localhost:8002/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_persona": {
      "name": "Ngozi",
      "location": "Abuja, Nigeria",
      "preferences": ["afrobeats", "fine dining", "self-improvement books"],
      "review_history": [
        {"item": "Nkoyo Restaurant", "rating": 5.0, "category": "restaurant"},
        {"item": "Burna Boy - African Giant", "rating": 5.0, "category": "music"}
      ]
    },
    "context": {"occasion": "Date night", "budget": "premium"},
    "num_recommendations": 5
  }'
```

### Task B Multi-turn: POST /recommend/chat

Pass a `conversation_id` from a previous response to continue the session. This lets users refine their request (e.g. "something cheaper" or "I meant books not restaurants").

---

## Datasets

The system was designed around the Yelp Open Dataset, Amazon Reviews, and Goodreads. A sample catalog is bundled in `shared/sample_catalog.py` covering restaurants, books, movies, music, and electronics. To swap in the full datasets, replace the items in that file and the FAISS index rebuilds automatically at startup.

---

## Interactive Docs

FastAPI generates interactive documentation automatically.

**Live (deployed):**
- Task A: https://dsn-bct-task-a-v9ik.onrender.com/docs
- Task B: https://dsn-bct-task-b-11lm.onrender.com/docs

**Local:**
- Task A: http://localhost:8001/docs
- Task B: http://localhost:8002/docs
