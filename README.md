# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

---

Coming to college can be a challenging and confusing process. On top of adjusting to academics, for most students, it is their first time living completely alone. At Brandeis University, first-year housing is mandatory, but in an attempt to simplify the official selection process, the university eliminates a lot of crucial, granular information from its public website - such as detailed floor plans, layout quirks, and building age realities. This lack of transparency can make new students feel more anxious and insecure about where they will live.

The Unofficial Guide will focus specifically on Brandeis first-year housing, covering the realities of roommate matching, physical housing options, and unwritten survival tips for incoming freshmen.

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 |Brandeis University - Information for First-Years, Midyears and Transfers|Offical Website| https://www.brandeis.edu/dcl/housing-on-campus/new-first-year/index.html|
| 2 |Brandeis University - Massell Quad|Offical Website| https://www.brandeis.edu/dcl/housing-on-campus/residence-halls/massell.html|
| 3 |Brandeis University - North Quad|Offical Website | https://www.brandeis.edu/dcl/housing-on-campus/residence-halls/north.html|
| 4 |Brandeis University - East Quad|Offical Website| https://www.brandeis.edu/dcl/housing-on-campus/residence-halls/east.html|
| 5 | Massell vs. North Quad Comprehensive Breakdown | Student Forum Thread - Reddit | https://www.reddit.com/r/brandeis/comments/1hfxjfr/dorms_and_housing/ |
| 6 | First-Year Quad & Building Attributes | Student Forum Thread - Reddit| https://www.reddit.com/r/brandeis/comments/1kgl5u2/freshman_dorms/ |
| 7 | The Freshman Roommate Matching Form Reality | Student Forum Thread - Reddit | https://www.reddit.com/r/brandeis/comments/1stwmdh/first_year_housing/ |
| 8 | Gordon Hall Natural Triple Structural Nuances | Student Forum Thread - Reddit | https://www.reddit.com/r/brandeis/comments/1mofavh/gordon_hall_double/ |
| 9 | Cable Hall Floor Assignment Logistics | Student Forum Thread - Reddit | https://www.reddit.com/r/brandeis/comments/w26pxh/cable_hall/ |
| 10 | The Infrastructure Reality Check (No A/C & Flooding Risk) | Student Forum Thread - Reddit | https://www.reddit.com/r/brandeis/comments/1bm9fal/dorms_amenities/ |
| 11 |Brandeis Considering Demolition of East Quad Following Completion of New Residence Hall |Student News Paper| https://brandeishoot.com/brandeis-considering-demolition-of-east-quad-following-completion-of-new-residence-hall/ |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 600

**Overlap:** 150

**Why these choices fit your documents:** My sources are highly diverse. Some are structured as medium-sized articles, such as the official university website and the school student newspaper (*The Brandeis Hoot*), where important context spans multiple sentences. On the other hand, Reddit sources include informal comments that are only a sentence or two long. Choosing a fixed baseline of 600 characters ensures that short Reddit posts remain fully intact within a single chunk, while a 150-character overlap prevents critical details from being cut in half and losing context when splitting the longer, official articles.

**Final chunk count:** 61

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

all-MiniLM-L6-v2, loaded locally via the sentence-transformers library. I chose it because it runs entirely on-machine with no API key and no rate limits, which fits a small, specialized data - Brandeis first-year housing. It produced 61 chuncks (which is a great amount for this size project), which are stored in ChromaDB

**Production tradeoff reflection:**

If I were deploying this for real users without cost constraints, I would think about moving it to a big hosted model like OpenAI's text-embedding-3-large. The main gains would be a larger context window — letting me embed entire multi-comment Reddit threads as single units instead of fragmenting them which would increase accuracy (on semantic, slang typos and specific school abbreviations). The tradeoffs would be per-query API cost, network latency, and a dependency on an external service. For a student project with a small corpus, all-MiniLM-L6-v2's locality and zero cost outweigh the accuracy ceiling. at scale, the vocabulary-gap problem (my Anticipated Challenge 1) would justify the upgrade.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

I enforce grounding primarily through the system prompt that is sent to Groq's model. The prompt gives explicit strict instructions rather than general suggestions. It tells the model to answer using only the provided context, avoid using outside knowledge such as: never invent dorm names, housing policies, or housing details, and return the exact phrase "I don't have enough information on that." whenever the retrieved documents do not contain enough information to answer the question. This allows the system to reject questions that fall outside the scope of the knowledge base rather than generating a plausible-sounding answer.

To make the retrieved information easier for the model to interpret, every chunk is labeled with its source before being inserted into the context window. Official university documents are tagged with their source URL, while student-generated content is tagged with its filename (converted to txt files as Reddit block scrapping request). This helps the model distinguish between official university information and student experiences or opinions when generating a response.

**How source attribution is surfaced in the response:**

Source attribution is handled programmatically rather than relying entirely on the language model. After retrieval, the ask() function collects and deduplicates the source names from the metadata of the chunks that were actually retrieved. These sources are then returned separately from the generated answer and displayed in the Gradio interface under a dedicated "Retrieved from" section.

I also instruct the model to reference sources within its response. For example, official information is cited as coming from the university website, while student perspectives are attributed to Reddit discussions. When both source types contribute to an answer, the model is instructed to clearly separate official information from student experiences. However, because the source list is generated directly from retrieval metadata, users can always see which documents were used even if the model's wording varies.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 |Which freshman housing is the best? | North and Massell offer better dorm facilities, however their locations provide different benefits. East Quad offers the worst facilities and is mostly used for overflow. | The system was able to highlight and diffrentiate between the different facilities in North and Massell but didn't mentioned East Quad.| Relevant | Partially accurate |
| 2 | How does the housing application work for freshmen, and what do students advise about the matching form? | Officially, students complete a lifestyle questionnaire on the DCL portal for random matching. Unofficially, students emphasize being completely honest about sleeping/cleanliness habits rather than answering ideally, to avoid bad pairings. | Cited official site for the First-Year Housing Application, then student forums for the lifestyle-form details and random roommate assignment. Missed the "don't lie on the form" advice. | Relevant | Partially accurate |
| 3 | What should incoming freshmen expect regarding storage and room layouts in the quads? |Official sites promise basic furniture, but students note that layouts vary wildly between quads. For example, some rooms have built-in open shelves over the beds and under-bed drawers, meaning floor layouts are highly dependent on which building you get. | Gave East Quad square footage from official site but then said it lacked storage info and partially refused. Missed the student details on built-in shelves / under-bed drawers. | Partially relevant | Partially accurate 
| 4 | What is a "forced triple" and which first-year building is it most commonly found in? | A forced triple is a standard double room that the university fills with three students due to high enrollment. Student warnings explicitly point out that these crowded setups are most common in Shapiro Hall. | Double filled with 3 students; most common in Shapiro | Correctly identified Shapiro as most common, but flagged that the definition isn't stated, and didn't try to guess | Relevant |Accurate|
| 5 | What happens if the main freshman quads fill up due to high enrollment? | When Brandeis over-admits a freshman class and Massell or North fill to capacity, first-year students face "overflow placement." This means they are assigned to live outside the designated freshman areas, typically in East Quad. | Cited official site (students assigned to Massell/North/East) plus student forums (East used when they run out of housing). Correct. | Relevant | Accurate |
| 6 (Out-of-scope question) | What is the meal plan price for first-year students? | Not enough information to answer the question | I don't have enough information on that.| I don't have enough information on that. | N/A | Accurate |

**Retrieval quality:** Relevant
**Response accuracy:** Accurate / Partially accurate


---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
