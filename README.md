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
| 5 | Massell vs. North Quad Comprehensive Breakdown | Student Forum Thread | https://www.reddit.com/r/brandeis/comments/1hfxjfr/dorms_and_housing/ |
| 6 | First-Year Quad Hierarchy & Building Attributes | Student Forum Thread | https://www.reddit.com/r/brandeis/comments/1kgl5u2/freshman_dorms/ |
| 7 | The Shapiro Forced Triple and Basement Warning | Student Forum Comment | https://www.reddit.com/r/brandeis/comments/1kgl5u2/freshman_dorms/ |
| 8 | The Freshman Roommate Matching Form Reality | Student Forum Thread | https://www.reddit.com/r/brandeis/comments/1stwmdh/first_year_housing/ |
| 9 | Gordon Hall Natural Triple Structural Nuances | Student Forum Thread | https://www.reddit.com/r/brandeis/comments/1mofavh/gordon_hall_double/ |
| 10 | Cable Hall Floor Assignment Logistics | Student Forum Thread | https://www.reddit.com/w26pxh/cable_hall/ |
| 11 | The Infrastructure Reality Check (No A/C & Flooding Risk) | Student Forum Thread | https://www.reddit.com/r/brandeis/comments/1bm9fal/dorms_amenities/ |
| 12 | Downstream Strategy: First-Year to Sophomore Lottery Shift | Student Forum Thread | https://www.reddit.com/r/brandeis/comments/1rndsdr/housing_numbers/ |
| 14 | The Truth About "Overflow" Placements | Student Forum Comment | https://www.reddit.com/r/brandeis/comments/1hfxjfr/dorms_and_housing/ |
| 15 |Brandeis Considering Demolition of East Quad Following Completion of New Residence Hall |Student News Paper| https://brandeishoot.com/brandeis-considering-demolition-of-east-quad-following-completion-of-new-residence-hall/ |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**

**Overlap:**

**Why these choices fit your documents:**

**Final chunk count:**

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

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
