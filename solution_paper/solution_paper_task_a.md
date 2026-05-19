# User Modeling and Review Generation for Nigerian Users Using LLM Agents

**DSN x BCT LLM Agent Challenge — Task A**


## Abstract

This paper describes the Task A agent: a system that simulates how a specific Nigerian user would write a review for an item they have never reviewed before, including the star rating and writing tone. The core motivation is that Nigerian users have a distinct voice online. They mix English and Pidgin, reference local geography, and are direct about price and value. Most review generation systems flatten this into a generic output. My approach puts behavioral profile and cultural context at the center of every generation decision, producing reviews that sound like the user actually wrote them.


## 1. Introduction

When you look at Nigerian users on platforms like Yelp or Amazon, you notice patterns that do not fit how most recommendation systems are designed. People write in a mix of English and Pidgin. They compare food to what their mothers cook. They mention the area of town, not just the city. They are very direct about price.

These are not noise signals. They are exactly the signals that make a review sound authentic versus generic.

Most systems collapse this richness into a number between 1 and 5. My approach for Task A was to preserve it. The review a user writes is as important as the rating they give, and a simulated review should feel like it came from that specific user, not from a generic model that read too many TripAdvisor entries.


## 2. System Design

### 2.1 Shared Foundation

Before building the Task A agent, I built three shared components that serve as its infrastructure.

**User Profiler**

This module takes a user's review history and extracts a structured behavioral profile. The fields I prioritised:

- Average rating and standard deviation, not just the average, because a person who gives 2s and 5s behaves very differently from someone who always gives 4s
- Average review length, because some users write two sentences and some write paragraphs, and a simulated review should match that
- Whether the user naturally writes in Nigerian Pidgin, detected by scanning history for markers like "abeg", "e dey", "na wa", "wahala"
- Their top categories from history

The last 3 reviews are passed directly into the prompt as style examples. I tried using all reviews but the prompts got too long and the model started averaging out the style instead of staying true to it. Using the most recent 3 worked better in practice.

**Nigerian Adapter**

This module generates cultural context injected into the system prompt. The decision to make it a separate module rather than inline prompt text was deliberate. It made it easier to test and tune independently of the core generation logic.

The adapter handles two things. First, city-level specificity: Lagos users reference Lekki, VI, Surulere; Abuja users reference Maitama, Wuse, Jabi. Using correct local geography makes output feel grounded. Second, code-switching calibration: if a user naturally mixes Pidgin, the adapter enables it; if they write in standard English, the adapter adds cultural awareness without forcing Pidgin, because that would actually hurt review quality for that user.

**Vector Store**

I used FAISS with sentence-transformer embeddings (all-MiniLM-L6-v2) for semantic retrieval. A keyword fallback is in place for environments where FAISS is unavailable. For Task A, the vector store supports item lookup when product metadata needs to be enriched.

### 2.2 Task A: Review Generation Agent

The problem Task A solves: given a user's history and an item they have never reviewed, what rating would they give it and how would they write about it?

**Workflow:**

1. Build the behavioral profile from the user's history via the User Profiler
2. Inject Nigerian cultural context based on their location and detected writing style via the Nigerian Adapter
3. Pass the profile, cultural context, and item metadata to the language model with a structured output requirement
4. Parse and validate the output

**Prompt Design**

The most important decision was showing the model the user's actual past reviews as examples, not just a summary of them. This keeps the tone specific. A user who writes "e sweet me die!" should not come out sounding like a formal TripAdvisor reviewer. The model sees concrete examples and stays close to them.

**Rating Calibration**

I constrain rating generation around the user's historical average and standard deviation. A user who consistently gives 3.5 to 4 stars should not generate a 5-star review unless the item clearly maps to something they explicitly love. The model is instructed to deviate from the mean only when the item presents a clear reason to.

**Output Format**

The agent returns structured JSON:

```json
{
  "rating": 4.0,
  "review": "Their suya na fire! Lekki location convenient. Price fair for the quality.",
  "reasoning": "User averages 4.0 for mid-range Nigerian spots..."
}
```

The reasoning field is not shown to end users but was essential during evaluation for understanding model behaviour.


## 3. Nigerian Contextualisation

The competition rubric offers bonus marks for content contextualised to behave and sound like Nigerians. I treated this as a serious design requirement, not an afterthought.

Nigeria is not one voice. A Lagos user from Surulere writes differently from one in Victoria Island. Forcing generic Pidgin on everyone produces reviews that feel like a caricature.

My approach:

1. Detect the user's actual writing style from their history before deciding how much Pidgin to enable
2. Use city-specific local references rather than just the city name
3. Frame value and price in a culturally accurate way, because Nigerian reviewers almost always mention whether something was worth the money
4. Include Nigerian-market items in the catalog: Nollywood films, Afrobeats albums, local restaurant chains, Nigerian-market electronics like Tecno and Infinix

One specific observation during testing: when the model was shown a user's actual Pidgin-inflected reviews as style examples, it naturally adopted the right level of code-switching without being explicitly told to. The Pidgin detection in the profiler is what enables or disables this pathway, but the model learns the specific style from the examples themselves.


## 4. Experiments and What I Learned

**Style examples vs summaries**

I initially summarised past reviews in the prompt ("this user tends to write positively about service and negatively about price"). The output was generic. Switching to including the raw reviews directly produced outputs that matched the user's tone much better.

**Rating calibration with standard deviation**

Early versions ignored rating standard deviation and just used the mean. This caused the model to always produce ratings close to the mean even for items that strongly matched or mismatched the user's preferences. Adding std to the prompt context and instructing the model to deviate when there is a clear reason gave more realistic rating distributions.

**Nigerian adapter as separate module vs inline**

Early versions baked the cultural context directly into the main prompt. Separating it into its own module made it much easier to tune the Nigerian context independently without touching the generation logic.


## 5. Limitations

The sample catalog is small. In production this would be backed by the full Yelp and Amazon datasets with millions of items. The current setup is designed to swap in the full datasets by replacing items in shared/sample_catalog.py and the FAISS index rebuilds automatically at startup.

The Nigerian adapter currently covers broad Nigerian Pidgin and the major cities. A more granular version would model regional variation more precisely, for example the difference between Lagos street Pidgin and Abuja's more formal code-switching patterns.

Automated evaluation of review quality requires human judgment or a fine-tuned evaluator model. The reasoning field helps with qualitative assessment but is not a substitute for a proper annotation study.


## 6. Conclusion

Task A is built on the thesis that users are not rows in a database. They have a voice, a context, and a culture. For Nigerian users specifically, that culture is specific enough that a system which ignores it produces outputs that feel foreign even when they are technically correct.

By putting behavioral profile and cultural context at the center of every generation decision rather than at the edge, the agent produces reviews that sound like the user actually wrote them. A review that captures the user's tone is more valuable than a review that only gets the number right.


## References

1. Yelp Inc. (2024). Yelp Open Dataset. yelp.com/dataset
2. He, R. and McAuley, J. (2016). Ups and Downs: Modeling the Visual Evolution of Fashion Trends. WWW 2016.
3. Wan, M. et al. (2019). Fine-Grained Spoiler Detection from Large-Scale Review Corpora. ACL 2019. (Goodreads dataset)
4. Reimers, N. and Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. EMNLP 2019.
5. Zhang, T. et al. (2020). BERTScore: Evaluating Text Generation with BERT. ICLR 2020.
