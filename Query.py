"""
query.py — Grounded generation for The Unofficial Guide (Brandeis housing RAG).

Implements Milestone 5 grounding requirements:
  - Answers come from retrieved context ONLY (system prompt enforces it).
  - Refuses ("I don't have enough information on that.") when context is insufficient.
  - Source attribution is GUARANTEED PROGRAMMATICALLY — sources are read from the
    retrieved chunks' metadata in code, not parsed out of the LLM's free text.

Pipeline stages (per planning.md architecture diagram):
    ... Retrieval -> Generation
        (ChromaDB)    (Groq llama-3.3-70b-versatile)

ask(question) -> {"answer": str, "sources": [filenames], "chunks": [retrieval dicts]}
is the single end-to-end entry point the Gradio interface calls.
"""

import os
from dotenv import load_dotenv
from groq import Groq

from retrieval import load_index, build_index, retrieve_housing_context, TOP_K

load_dotenv()  # reads GROQ_API_KEY from .env

LLM_MODEL = "llama-3.3-70b-versatile"   # Milestone 5 recommended default

# --- Grounding system prompt: ENFORCES context-only answering + refusal ---
SYSTEM_PROMPT = """You are an assistant that answers questions about Brandeis University \
first-year housing using ONLY the provided context documents.

STRICT RULES:
1. Answer using ONLY information found in the CONTEXT below. Do NOT use any outside or \
prior knowledge about Brandeis or college housing in general.
2. If the context does not contain enough information to answer the question, respond with \
EXACTLY: "I don't have enough information on that."
3. Do not invent dorm names, policies, amenities, or details that are not in the context.
4. When the context contains conflicting views (e.g. an official description vs. a student \
opinion), present both rather than picking one.
5. Be concise and factual. Do not speculate.
6. When citing sources, embed the source filename in parentheses immediately after \
your attribution phrase, like this: \
'According to students on Reddit (source: First-Year Quad Hierarchy & Building Attributes.txt), ...' \
or 'According to the official Brandeis website (source: OFFICIAL_East_Quad.txt), ...'. \
Use the exact filename from the (source: ...) label in the context. \
NEVER say 'according to the context' or 'according to the documents'.
7. Always check ALL context chunks, not just the first one. If multiple sources \
support the same point, cite them together: \
'According to both the official Brandeis website (source: OFFICIAL_New_FirstYear_Housing.txt) \
and students on Reddit (source: Massell vs. North Quad.txt), ...'. \
If sources say different things, present both perspectives separately."""

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


def _format_context(chunks):
    """
    Build the context block the LLM sees. Each chunk is labeled with its source
    FILENAME (not a number), so when the model attributes information in its prose
    it names the actual document. The authoritative source list is still assembled
    separately in ask() from metadata.
    """
    blocks = []
    for c in chunks:
        blocks.append(f"(source: {c['source']})\n{c['text']}")
    return "\n\n".join(blocks)


def ask(question, k=TOP_K):
    """
    End-to-end grounded query:
      1. Retrieve top-k chunks for the question.
      2. Generate an answer constrained to those chunks.
      3. Attach the source filenames PROGRAMMATICALLY from chunk metadata.

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
        "What is a forced triple and which building is it most common in?",
        "What do students advise about the roommate matching form?",
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