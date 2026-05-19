# Personalised Recommendation for Nigerian Users Using an LLM Agent

**DSN x BCT LLM Agent Challenge — Task B**

---

## Abstract

This paper describes the Task B agent: a personalised recommendation system for Nigerian users built around an agentic reasoning loop. Rather than returning the top results from a single vector search, the agent iteratively searches, evaluates candidates, and reasons about fit before committing to a final ranked list. It also supports multi-turn conversation, letting users refine requests across turns. The key insight is that a good recommendation for a Nigerian user requires cross-domain thinking and culturally grounded reasoning — not just a dot product on a history vector.

---

## 1. Introduction

Standard collaborative filtering asks: what do similar users like? It works reasonably well for popular items in well-represented demographics. It works poorly when the user base is underrepresented in training data, when a user's preferences span multiple domains, or when the right recommendation requires understanding context — occasion, budget, mood — not just past behaviour.

Nigerian users face all three of these problems. A user who loves Afrobeats and fine dining and self-improvement books cannot be served well by a system that picks the most popular item in each category. The best recommendation for a Saturday evening in Abuja might involve combining all three signals in a way that no single category search surfaces.

We built Task B to solve this with an agentic loop: a model that can search multiple times, reconsider, and construct a recommendation list the way a knowledgeable friend would — not the way a retrieval pipeline would.

---

## 2. System Design

### 2.1 Shared Foundation

Task B shares its infrastructure with Task A across three components.

**User Profiler**

Extracts a structured behavioral profile from the user's review history: average rating and standard deviation, average review length, Pidgin usage detection, and top categories. For Task B, the category distribution is particularly important — it tells the agent where to start its search and how to weight cross-domain candidates.

**Nigerian Adapter**

Generates cultural context injected into the system prompt. For Task B, this means grounding recommendations in local geography (specific Lagos or Abuja neighbourhoods), including Nigerian-market items in the catalog (Nollywood, Afrobeats, local restaurant chains, Tecno/Infinix electronics), and calibrating the personalized reasoning to reference things the user would actually recognise.

**Vector Store**

FAISS with sentence-transformer embeddings (all-MiniLM-L6-v2) for semantic retrieval. A keyword fallback is available for environments where FAISS is unavailable. The vector store is the primary retrieval mechanism the Task B agent calls during its reasoning loop.

### 2.2 Task B: Recommendation Agent

**The Agentic Loop**

The agent has three tools available:

- **search_items** — takes a natural language query and optional category filter, runs it through the vector store, returns candidate items
- **get_item_details** — fetches full metadata for a specific item
- **finalize_recommendations** — the termination tool the model calls when it is done reasoning, returning the final ranked list

The agent runs for up to 8 iterations. In practice it uses 3 to 5, performing multiple searches across different domains before settling on a final list. This is the key difference from a standard retrieval approach.

A user who loves Afrobeats and fine dining might trigger searches under music, restaurants, and then a cross-domain query like "upscale evening experience Abuja" — the last query surfaces items that neither single-domain search would find.

**Personalised Reasoning**

The agent is explicitly required to write personalised reasoning for each recommended item. Not "this is a popular restaurant" but "you gave Nkoyo a 5-star, which tells us your bar is high — this place is in that same tier." This makes the output feel like it came from someone who knows the user, not from a pipeline.

**Cold Start Handling**

When a user has no review history, the system prompt flags this and instructs the agent to rely on stated preferences, location, and demographic signals instead. The agent is required to report what strategy it used in the `cold_start_strategy` field of the response.

**Multi-turn Conversation**

The `/recommend/chat` endpoint maintains conversation history per session using a `conversation_id`. A user can follow up with "actually I want something cheaper" or "I meant books not restaurants" and the agent has full context from the previous turn. This is implemented by passing the prior message history back into the model context on each turn.

**Output Format**

```json
{
  "recommendations": [
    {
      "item": "Nkoyo Restaurant",
      "category": "restaurant",
      "score": 0.94,
      "reasoning": "You gave similar fine dining spots a 5-star. This is in that tier."
    }
  ],
  "search_iterations": 4,
  "cold_start_strategy": null
}
```

---

## 3. Nigerian Contextualisation

The competition rubric offers bonus marks for content contextualised to behave and sound like Nigerians. For Task B this shaped both the catalog and the reasoning style.

**Catalog**

The sample catalog includes items that are relevant to Nigerian users: Nollywood films, Afrobeats albums, local restaurant chains, Nigerian-market electronics (Tecno, Infinix), and venues in Lagos and Abuja neighbourhoods rather than just city-level references.

**Reasoning tone**

The agent's personalised reasoning is calibrated to reference things a Nigerian user would recognise. Price-consciousness is always considered — Nigerian reviewers almost always mention whether something was worth the money, and the agent follows this pattern when explaining recommendations.

**Geography**

City-level specificity matters. Lagos and Abuja are not interchangeable. The agent uses neighbourhood-level references (Lekki, VI, Maitama, Wuse) when they are available from item metadata, making recommendations feel geographically grounded.

---

## 4. Experiments and What We Learned

**Single search vs agentic loop**

We tested a simpler version that performed one vector search and returned the top results. The recommendations were reasonable but lacked cross-domain coverage and the reasoning was shallow because the model only saw a narrow candidate pool. The agentic loop consistently produced more varied and better-explained recommendations by iterating across domains before finalising.

**Number of iterations**

Setting the cap at 8 iterations was a practical choice. Below 3, the agent sometimes did not explore enough domains. Above 8, there were diminishing returns and occasional loops where the model re-searched similar queries. In practice the agent converges in 3 to 5 iterations on most user profiles.

**Nigerian adapter as separate module vs inline**

Early versions baked the cultural context directly into the main prompt. Separating it into its own module made it much easier to tune the Nigerian contextualisation independently without touching the agent's tool-use logic.

---

## 5. Limitations

The sample catalog is small. In production this would be backed by the full Yelp and Amazon datasets with millions of items, and the FAISS index would use approximate nearest neighbour search for scale. The current setup uses exact search, which is appropriate at this catalog size.

NDCG@10 cannot be computed offline without a held-out ground truth relevance set. The infrastructure is in place and the system is designed to be evaluated against the competition's test set.

Multi-turn conversation state is currently in-memory. A production system would persist session state to a database.

The Nigerian adapter covers broad Nigerian Pidgin and the major cities. Regional variation — for example the difference between Lagos and Kano code-switching patterns — would require a more granular model.

---

## 6. Conclusion

Task B is built on the observation that the best recommendations require reasoning, not just retrieval. A user's preferences span domains and contexts that a single vector search cannot bridge. The agentic loop gives the model space to explore, reconsider, and construct a list the way a knowledgeable friend would.

Grounding this in Nigerian cultural context — local geography, Nigerian-market items, value-conscious reasoning — makes the output feel relevant to the actual user rather than to a generic global profile.

---

## References

1. Yelp Inc. (2024). Yelp Open Dataset. yelp.com/dataset
2. He, R. and McAuley, J. (2016). Ups and Downs: Modeling the Visual Evolution of Fashion Trends. WWW 2016.
3. Wan, M. et al. (2019). Fine-Grained Spoiler Detection from Large-Scale Review Corpora. ACL 2019. (Goodreads dataset)
4. Reimers, N. and Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. EMNLP 2019.
5. Yao, S. et al. (2023). ReAct: Synergizing Reasoning and Acting in Language Models. ICLR 2023.
6. Johnson, J. et al. (2021). Billion-scale similarity search with GPUs. IEEE Transactions on Big Data.
