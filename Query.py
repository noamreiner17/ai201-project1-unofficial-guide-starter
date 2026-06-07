import os
from dotenv import load_dotenv
from groq import Groq
from ingest import OFFICIAL_SOURCES 

from retrieval import load_index, build_index, retrieve_housing_context, TOP_K

load_dotenv()  # reads GROQ_API_KEY from .env

LLM_MODEL = "llama-3.3-70b-versatile" 

SYSTEM_PROMPT = """You are an assistant that answers questions about Brandeis University \
first-year housing using ONLY the provided context documents.

STRICT RULES:
1. Answer using ONLY information found in the CONTEXT below. Do NOT use any outside or \
prior knowledge about Brandeis or college housing in general.
2. If the context does not contain enough information to answer the question, respond with \
EXACTLY: "I don't have enough information on that."
3. Do not invent dorm names, policies, amenities, or details that are not in the context.
4. Be concise and factual. Do not speculate.
5. Each context chunk is labeled with a (source: ...) line. Files whose names start with \
'OFFICIAL_' are the official Brandeis website. All other files are student forum posts. \
Always check ALL chunks, not just the first one, before answering.
6. Format your attribution based on which source types the answer draws from:
   - If the answer comes ONLY from OFFICIAL_ files: start with \
"According to the official website (URL)," using the exact URL shown in that chunk's \
(source: ...) label, then give the answer.
   - If the answer comes ONLY from non-OFFICIAL_ files: start with \
"According to student forums (filename)," using the exact filename, then give the answer.
   - If the answer draws from BOTH types: start with the official source first as above, \
then continue with "However, " if the student posts CONTRADICT the official information, \
or "Additionally, " if the student posts AGREE WITH or ADD non-contradicting detail, \
followed by the student attribution and their information.
7. NEVER say "according to the context" or "according to the documents." Always use the \
specific attribution format from rule 6."""

USER_TEMPLATE = """CONTEXT:
{context}

QUESTION: {question}

Answer using only the context above. If the context is insufficient, say \
"I don't have enough information on that." """


# Module-level handles so the LLM client and index load once, not per query.
_client = None
_collection = None
_embedder = None


def _init():
    """Lazy-init the Groq client and the vector index (build if missing)."""
    global _client, _collection, _embedder
    if _client is None:
        _client = Groq(api_key=os.environ["GROQ_API_KEY"])
    if _collection is None:
        try:
            _collection, _embedder = load_index()   # use existing ./chroma_db
        except Exception:
            _collection, _embedder = build_index()   # first run: build it
    return _client, _collection, _embedder


#formating the matadata for the LLM to use in its answer generation.
def _format_context(chunks):
    blocks = []
    for c in chunks:
        src = c["source"]
        if src in OFFICIAL_SOURCES:
            label = f"(source: {src} | URL: {OFFICIAL_SOURCES[src]})"
        else:
            label = f"(source: {src})"
        blocks.append(f"{label}\n{c['text']}")
    return "\n\n".join(blocks)


def ask(question, k=TOP_K):
    """
    End-to-end grounded query:
      1. Retrieve top-k chunks for the question.
      2. Generate an answer constrained to those chunks.
      3. Attach the source filenames from chunk metadata.

    Returns {"answer", "sources", "chunks"}.
    """
    client, collection, embedder = _init()
    chunks = retrieve_housing_context(question, collection, embedder, k=k)

    # Programmatic source attribution: dedup the source filenames of the chunks
    # we actually retrieved. This is GUARANTEED regardless of what the LLM writes.
    sources = list(dict.fromkeys(c["source"] for c in chunks))

    context = _format_context(chunks)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_TEMPLATE.format(context=context, question=question)},
    ]

    resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.1,   # low temp keeps it close to the context, less invention
    )
    answer = resp.choices[0].message.content.strip()
    

    # If the model refused, don't attach sources (nothing was actually used).
    if answer.lower().startswith("i don't have enough information"):
        sources = []

    return {"answer": answer, "sources": sources, "chunks": chunks}


if __name__ == "__main__":
    # End-to-end grounding test on eval queries + one out-of-scope question.
    tests = [
        "Which freshman housing is the best?",
        "How does the housing application work / matching form advice?",
        "Storage and room layouts in the quads?",
        "What is a forced triple and which building is it most common in?",
        "What happens if the freshman quads fill up due to high enrollment?",
        "What is the meal plan price for first-year students?",   # out-of-scope -> should refuse
    ]
    for q in tests:
        print("\n" + "=" * 72)
        print(f"Q: {q}")
        print("=" * 72)
        r = ask(q)
        print(f"\nANSWER:\n{r['answer']}\n")
        print(f"SOURCES (programmatic): {r['sources']}")
        print(f"distances: {[round(c['distance'], 3) for c in r['chunks']]}")