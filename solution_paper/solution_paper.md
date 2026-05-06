# User Modeling and Personalised Recommendation for Nigerian Users Using LLM Agents

**DSN x BCT LLM Agent Challenge**
**Submission Deadline: 24 May 2026**

---

## Abstract

This paper describes a two-agent system for user modeling and personalised recommendation, built with a focus on Nigerian users. Task A generates reviews that simulate how a specific user would write about an item they have never reviewed before, including the star rating and writing tone. Task B generates ranked recommendations using an agentic search and reasoning workflow that goes beyond matching categories. The key motivation behind both systems is that Nigerian users are not generic users. They have a distinct way of writing online, specific cultural reference points, and a value-consciousness that most global models completely ignore. We built this into the system from the start, not as an afterthought.

---

## 1. Introduction

When you look at Nigerian users on platforms like Yelp or Amazon, you notice patterns that do not fit how most recommendation systems are designed. People write in a mix of English and Pidgin. They compare food to what their mothers cook. They mention the area of town the place is in, not just the city. They are very direct about price.

These are not noise signals. They are exactly the signals that make a review sound authentic versus generic.

Most systems collapse this richness into a number between 1 and 5. Our approach was to preserve it. The review a user writes is as important as the rating they give, and the recommendation a system returns should feel like it came from someone who actually knows the user, not just someone who ran a dot product on their history vector.

We built two containerised agents that embody this philosophy, using the Yelp, Amazon Reviews, and Goodreads datasets as the behavioral foundation, and a shared Nigerian cultural context layer that runs across both tasks.

---

## 2. System Design

### 2.1 The Shared Foundation

Before building either agent, we built three shared components that both tasks depend on.

**User Profiler**

This module takes a user's review history and extracts a structured behavioral profile. The fields we cared most about were:

- Average rating and standard deviation (not just the average, because a person who gives 2s and 5s behaves very differently from someone who always gives 4s)
- Average review length, because some users write two sentences and some write paragraphs, and a simulated review should match that
- Whether the user naturally writes in Nigerian Pidgin, which we detect by scanning their history for markers like "abeg", "e dey", "na wa", "wahala"
- Their top categories from history

The last 3 reviews are passed directly into the prompt as style examples. We tried using all reviews but the prompts got too long and the model started averaging out the style instead of staying true to it. Using the most recent 3 worked better in practice.

**Nigerian Adapter**

This module generates cultural context that gets injected into the system prompt for both agents. The decision to make this a separate module rather than inline prompt text was deliberate. It made it easier to test and tune independently of the core generation logic.

The adapter handles two things. First, city-level specificity. Lagos users reference Lekki, VI, Surulere. Abuja users reference Maitama, Wuse, Jabi. Using the correct local geography makes the output feel grounded instead of generic. Second, it handles code-switching calibration. If a user naturally mixes Pidgin into their reviews, the adapter enables that. If they write in standard English, the adapter adds cultural awareness without forcing Pidgin into the output because that would actually hurt the review quality for that user.

**Vector Store**

We used FAISS with sentence-transformer embeddings (all-MiniLM-L6-v2) for semantic retrieval. The reason for semantic search over keyword search is simple: a query like "something relaxing for a Sunday in Abuja" should surface relevant results even if none of those words appear in the item description. We kept a keyword fallback for environments where FAISS is unavailable.

### 2.2 Task A: User Modeling

The problem Task A solves is: given a user's history and an item they have never reviewed, what rating would they give it and how would they write about it?

Our workflow is:

1. Build the behavioral profile from their history
2. Inject Nigerian cultural context based on their location and writing style
3. Pass the profile, cultural context, and item metadata to the language model with a structured output requirement
4. Parse and validate the output

The most important prompt design decision was showing the model the user's actual past reviews as examples, not just a summary of them. This keeps the tone specific. A user who writes "e sweet me die!" should not come out sounding like a TripAdvisor reviewer. The model sees concrete examples and stays close to them.

We also constrain the rating generation around the user's historical average and standard deviation. A user who consistently gives 3.5 to 4 stars should not generate a 5-star review unless the item clearly maps to something they love.

The output is structured JSON with rating, review text, and a reasoning field. The reasoning field is not shown to end users but is useful for understanding what the model was doing, which helped a lot during evaluation.

### 2.3 Task B: Recommendation

Task B uses an agentic loop with three tools the model can call:

- **search_items** takes a natural language query and an optional category filter, runs it through the vector store, and returns candidate items
- **get_item_details** fetches full metadata for a specific item
- **finalize_recommendations** is the termination tool the model calls when it is done reasoning

The agent runs for up to 8 iterations. In practice it usually uses 3 to 5, doing multiple searches across different domains before settling on a final list. This is the key difference from a standard retrieval approach. A user who loves Afrobeats and fine dining might get recommendations searched under music, restaurants, and then a cross-domain query like "upscale evening experience Abuja" that surfaces things neither single-domain search would find.

The agent is also explicitly told to write personalized reasoning for each item. Not "this is a popular restaurant" but "you gave Nkoyo a 5-star, which tells us your bar is high, and this is in that same tier."

**Cold start handling**: when a user has no review history, the system prompt flags this and tells the agent to rely on stated preferences, location, and demographic signals instead. The agent is also required to report what strategy it used in the cold_start_strategy field.

**Multi-turn**: the /recommend/chat endpoint maintains conversation history per session. A user can follow up with "actually I want something cheaper" and the agent has full context from the previous turn.

---

## 3. Nigerian Contextualisation

The competition rubric offers bonus marks for content that is contextualised to behave and sound like Nigerians. We treated this as a serious design requirement.

The challenge is that Nigeria is not one voice. A Lagos user from Surulere writes differently from one in Victoria Island. A user from Kano code-switches differently from one in Port Harcourt. Forcing generic Pidgin on everyone produces reviews that feel like a caricature.

Our approach was to:

1. Detect the user's actual writing style from their history before deciding how much Pidgin to enable
2. Use city-specific local references rather than just the city name
3. Frame value and price in a culturally accurate way, because Nigerian reviewers almost always mention whether something was worth the money
4. Include Nigerian-market items in the catalog: Nollywood films, Afrobeats albums, local restaurant chains, Nigerian market electronics like Tecno and Infinix

One specific thing we noticed during testing: when the model was shown a user's actual Pidgin-inflected reviews as style examples, it naturally adopted the right level of code-switching without being told to. The detection logic in the profiler is what enables or disables this, but the model learns the specific style from the examples themselves.

---

## 4. Experiments and What We Learned

**Style examples vs summaries**: We initially summarised the user's past reviews in the prompt ("this user tends to write positively about service and negatively about price"). The output was generic. Switching to including the raw reviews directly produced outputs that matched the user's tone much better.

**Rating calibration**: Early versions ignored rating standard deviation and just used the mean. This caused the model to always produce ratings close to the mean even for items that strongly matched or mismatched the user's preferences. Adding std to the prompt context and instructing the model to deviate when there is a clear reason gave more realistic distributions.

**Single search vs agentic loop for Task B**: We tested a simple version that did one vector search and returned the top results. The recommendations were reasonable but lacked cross-domain coverage and the reasoning was shallow. The agentic loop consistently produced more varied and better-explained recommendations.

**Nigerian adapter as separate module vs inline**: Early versions baked the cultural context directly into the main prompt. Separating it into its own module made it much easier to tune and test the Nigerian context independently without touching the generation logic.

---

## 5. Limitations

The sample catalog is small. In production this would be backed by the full Yelp and Amazon datasets with millions of items, and the FAISS index would use approximate nearest neighbour search for scale. The current setup uses exact search which is fine at this catalog size.

NDCG@10 cannot be computed offline without a held-out ground truth relevance set. The infrastructure is in place and the system is designed to be evaluated against the competition's test set.

The Nigerian adapter currently covers broad Nigerian Pidgin and the major cities. A more granular version would model regional variation more precisely, for example the difference between Lagos street Pidgin and Abuja more formal code-switching patterns.

---

## 6. Conclusion

The thesis of this work is that users are not rows in a database. They have a voice, a context, and a culture. For Nigerian users specifically, that culture is specific enough that a system which ignores it will produce outputs that feel foreign even when they are technically correct.

The two agents we built try to solve this by putting behavioral profile and cultural context at the center of every generation decision, not at the edge. The results we saw during testing suggest this is the right direction. A review that sounds like the user actually wrote it is more valuable than a review that just gets the number right.

---

## References

1. Yelp Inc. (2024). Yelp Open Dataset. yelp.com/dataset
2. He, R. and McAuley, J. (2016). Ups and Downs: Modeling the Visual Evolution of Fashion Trends. WWW 2016.
3. Wan, M. et al. (2019). Fine-Grained Spoiler Detection from Large-Scale Review Corpora. ACL 2019. (Goodreads dataset)
4. Reimers, N. and Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. EMNLP 2019.
5. Zhang, T. et al. (2020). BERTScore: Evaluating Text Generation with BERT. ICLR 2020.
6. Yao, S. et al. (2023). ReAct: Synergizing Reasoning and Acting in Language Models. ICLR 2023.
7. Johnson, J. et al. (2021). Billion-scale similarity search with GPUs. IEEE Transactions on Big Data.
