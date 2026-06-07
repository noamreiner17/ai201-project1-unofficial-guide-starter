# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

The domain I chose is an unofficial guide for first-year undergraduate housing. This knowledge is incredibly valuable because coming to college well-prepared can drastically ease a student's transition into their academic year and significantly reduce overall stress. Official university channels will not necessarily highlight the downsides, structural flaws, or practical tricks of moving into campus dorms, as doing so does not benefit their institutional image. Therefore, unofficial channels is essential to increasing the readiness and confidence of incoming students.

---

## Documents

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Brandeis University - Information for First-Years, Midyears and Transfers | Official guidance on housing policies, timelines, and basic first-year setups. | https://www.brandeis.edu/dcl/housing-on-campus/new-first-year/index.html |
| 2 | Brandeis University - Massell Quad | Official university descriptions of amenities and halls within Massell Quad. | https://www.brandeis.edu/dcl/housing-on-campus/residence-halls/massell.html |
| 3 | Brandeis University - North Quad | Official university descriptions of layouts and features of North Quad buildings. | https://www.brandeis.edu/dcl/housing-on-campus/residence-halls/north.html |
| 4 | Brandeis University - East Quad | Official university page detailing East Quad's facilities and traditional setups. | https://www.brandeis.edu/dcl/housing-on-campus/residence-halls/east.html |
| 5 | Massell vs. North Quad Comprehensive Breakdown | Student forum thread debating geographic realities, hills, and dining hall proximities. | https://www.reddit.com/r/brandeis/comments/1hfxjfr/dorms_and_housing/ |
| 6 | First-Year Quad Hierarchy & Building Attributes | Student thread forming an explicit tier-list of buildings based on flooring and desk space. | https://www.reddit.com/r/brandeis/comments/1kgl5u2/freshman_dorms/ |
| 7 | The Shapiro Forced Triple and Basement Warning | Student forum comment detailing room congestion and the lack of third-floor elevators. | https://www.reddit.com/r/brandeis/comments/1kgl5u2/freshman_dorms/ |
| 8 | The Freshman Roommate Matching Form Reality | Discussion regarding how random matching works and the honesty needed for lifestyle forms. | https://www.reddit.com/r/brandeis/comments/1stwmdh/first_year_housing/ |
| 9 | Gordon Hall Natural Triple Structural Nuances | Deep student dive explaining storage configurations and missing floor plan realities. | https://www.reddit.com/r/brandeis/comments/1mofavh/gordon_hall_double/ |
| 10 | Cable Hall Floor Assignment Logistics | Mapping of floor structures, bathroom assignments, and laundry access within Cable Hall. | https://www.reddit.com/w26pxh/cable_hall/ |
| 11 | The Infrastructure Reality Check (No A/C & Flooding Risk) | Direct student warnings concerning zero air conditioning and flooding risks in basement rooms. | https://www.reddit.com/r/brandeis/comments/1bm9fal/dorms_amenities/ |
| 12 | Downstream Strategy: First-Year to Sophomore Lottery Shift | Student explanation of how freshman choices impacts the sophomore housing lottery numbers. | https://www.reddit.com/r/brandeis/comments/1rndsdr/housing_numbers/ |
| 14 | The Truth About "Overflow" Placements | Commentary addressing over-admissions and the reality of being placed outside standard quads. | https://www.reddit.com/r/brandeis/comments/1hfxjfr/dorms_and_housing/ |
| 15 | Brandeis Considering Demolition of East Quad Following Completion of New Residence Hall | Student newspaper investigative piece about shifts in the physical housing campus footprint. | https://brandeishoot.com/brandeis-considering-demolition-of-east-quad-following-completion-of-new-residence-hall/ |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 600 characters  

**Overlap:** 150 characters  

**Reasoning:** My sources are highly diverse. Some are structured as medium-sized articles, such as the official university website and the school student newspaper (*The Brandeis Hoot*), where important context spans multiple sentences. On the other hand, Reddit sources include informal comments that are only a sentence or two long. Choosing a fixed baseline of 600 characters ensures that short Reddit posts remain fully intact within a single chunk, while a 150-character overlap prevents critical details from being cut in half and losing context when splitting the longer, official articles.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers

**Top-k:** 6

**Production tradeoff reflection:**
I am using all-MiniLM-L6-v2 because it runs locally, has low latency, and is highly efficient for a small-scale specialized dataset like Brandeis housing (small school :)). I selected a top-k of 4 chunks because my domain relies on contrasting perspectives (offical and unoffical sources). Retrieving 4 chunks ensures that the user can anticipate information from both sides.

If deploying this at scale without cost constraints, I would upgrade to a commercial model like text-embedding-3-large. This would provide a larger context window to ingest entire multi-comment Reddit threads without fragmenting them, and offer better semantic accuracy when interpreting messy student slang, typos, and specific campus abbreviations.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Which freshman housing is the best? | North and Massell offer better dorm facilities, however their locations provide different benefits. East Quad offers the worst facilities and is mostly used for overflow. |
| 2 | How does the housing application work for freshmen, and what do students advise about the matching form? | Officially, students complete a lifestyle questionnaire on the DCL portal for random matching. Unofficially, students emphasize being completely honest about sleeping/cleanliness habits rather than answering ideally, to avoid bad pairings. |
| 3 | What should incoming freshmen expect regarding storage and room layouts in the quads? | Official sites promise basic furniture, but students note that layouts vary wildly between quads. For example, some rooms have built-in open shelves over the beds and under-bed drawers, meaning floor layouts are highly dependent on which building you get. |
| 4 | What is a "forced triple" and which first-year building is it most commonly found in? | A forced triple is a standard double room that the university fills with three students due to high enrollment. Student warnings explicitly point out that these crowded setups are most common in Shapiro Hall. |
| 5 | What happens if the main freshman quads fill up due to high enrollment? | When Brandeis over-admits a freshman class and Massell or North fill to capacity, first-year students face "overflow placement." This means they are assigned to live outside the designated freshman areas, typically in East Quad. |




---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Hyper-Local Abbreviations, Isolated Hall Names, and Student Slang:** Incoming freshmen will likely search for broad terms like "Massell Quad" or "North Quad," but seasoned students on Reddit rarely use those official quad names. Instead, they drop abbreviations, specific building names like "Shapiro," "DeRoy," "Usen," or "Cable" without explicitly stating which quad they belong to. Because standard embedding models look for semantic similarity, a chunk that only mentions "Usen features tile floors" might not rank highly when a user searches for "Massell Quad layout." This language gap between official administrative terms and shorthand student slang risks burying the exact answers the user is looking for.

2. **Conflicting Official vs. Unofficial information:** Because the dataset deliberately contrasts university text with raw student reviews, the LLM will frequently encounter contradictory information within the retrieved context.
---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

![RAG Pipeline Diagram](pineline.png)

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**


 - Gemini: during sourcing to find relevant Reddit threads and official Brandeis housing pages, and to filter which discussions had substantive content.

 - Claude:
     Building the ingestion script: gave it my Chunking Strategy (600 chars / 150 overlap) and document types (Reddit exports + official pages), asked for a RecursiveCharacterTextSplitter implementation.

     It produced chunk_documents() — loads.txt files, strips boilerplate/HTML, chunks with my parameters, attaches source + chunk_index metadata.

     I overrode: removed JSONL step so it reads files directly (keeping the project complexity low), and merged the official-page fetching into the script as a built-in first stage. Verified by printing sample chunks and confirming clean cuts + no leftover boilerplate.

**Milestone 4 — Embedding and retrieval:**

 - Claude: Used for my Retrieval Approach section (all-MiniLM-L6-v2, persistent ChromaDB, source metadata).
     It produced the embedding script and retrieve_housing_context(), returning top-k chunks with distances and sources.

     Testing showed Q5 (overflow → East Quad) didn't surface at top-k = 4 because the fact was buried in a North Quad chunk.

     I overrode: raised top-k from 4 to 6 and updated planning.md.

**Milestone 5 — Generation and interface:**

  - Claude:

     Used Claude with my grounding requirement + the example citation format. Asked for the system prompt, ask() function, and Gradio UI.

     It produced a strict context-only system prompt with a fixed refusal string, an ask() that builds the source list programmatically from metadata, and a working Gradio interface.
     
     I iterated on citation formatting — the model kept saying "according to the context" and "Document N."
     I restructured the prompt - label context by filename not number, distinguish official ("official website") from student ("student forums") sources, and use a "However"/"Additionally" structure when both source types contribute.