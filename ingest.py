import os
import re
import html
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# --- Spec values from planning.md (Chunking Strategy section) ---
CHUNK_SIZE = 600
CHUNK_OVERLAP = 150

# ----------------------------------------------------------------------------- #
# STAGE 1: LOAD                                                                  #
# ----------------------------------------------------------------------------- #
def load_documents(directory_path: str):
    """
    Load every .txt file from disk as raw text (no cleaning yet).
    Returns: list of {"source": filename, "raw": text}.
    """
    raw_docs = []
    for fname in sorted(os.listdir(directory_path)):
        if not fname.lower().endswith(".txt"):
            continue
        with open(os.path.join(directory_path, fname), "r", encoding="utf-8") as f:
            raw_docs.append({"source": fname, "raw": f.read()})
    return raw_docs


# ----------------------------------------------------------------------------- #
# STAGE 2: CLEAN                                                                 #
# ----------------------------------------------------------------------------- #
def clean_text(raw: str) -> str:
    """
    Clean a raw document into substantive content ready for chunking.

    REMOVES:
      - Speaker-label boilerplate ("Student comment:", "Student question:") that
        prefixes every post and repeats across every file — pure boilerplate.
      - HTML tags and HTML entities (&amp;, &nbsp;, &#39; ...). None appear in the
        current forum-export corpus, but this makes the cleaner safe if official
        Brandeis web pages are added later.
      - Excess whitespace / blank lines, so the splitter sees real paragraph breaks.

    KEEPS:
      - All review text, opinions, layout descriptions, hall names, floor numbers,
        and dining-hall context — the substantive content the RAG system answers from.
    """
    text = raw

    # Strip HTML tags if any slipped in (e.g., from a future scraped page).
    text = re.sub(r"<[^>]+>", "", text)

    # Decode HTML entities (&amp; -> &, &#39; -> ', &nbsp; -> space).
    text = html.unescape(text)

    # Remove the repeated speaker-label boilerplate at the start of any line.
    text = re.sub(r"(?im)^\s*student\s+(comment|question)\s*:\s*", "", text)

    # Normalize line endings, then collapse 3+ newlines to a single paragraph break.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)        # trailing spaces on lines
    text = re.sub(r"[ \t]{2,}", " ", text)        # runs of spaces

    return text.strip()


def clean_documents(raw_docs):
    """Clean every raw doc; skip any that become empty. Returns list of {source, text}."""
    cleaned = []
    for d in raw_docs:
        text = clean_text(d["raw"])
        if not text:
            print(f"[skip] {d['source']} produced empty text after cleaning")
            continue
        cleaned.append({"source": d["source"], "text": text})
    return cleaned


# ----------------------------------------------------------------------------- #
# STAGE 3: CHUNK (planning.md spec: 600 / 150)                                   #
# ----------------------------------------------------------------------------- #
def chunk_documents(directory_path: str):
    """
    Full pass: load -> clean -> chunk -> attach metadata.
    Returns: list[Document] with metadata {"source", "chunk_index"}.
    """
    raw_docs = load_documents(directory_path)
    cleaned = clean_documents(raw_docs)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],   # paragraph -> line -> sentence -> word -> char
        length_function=len,
    )

    all_chunks = []
    for d in cleaned:
        for i, piece in enumerate(splitter.split_text(d["text"])):
            if not piece.strip():
                continue
            all_chunks.append(
                Document(
                    page_content=piece,
                    metadata={"source": d["source"], "chunk_index": i},
                )
            )
    return all_chunks


# ----------------------------------------------------------------------------- #
# STAGE 4: INSPECT                                                               #
# ----------------------------------------------------------------------------- #
if __name__ == "__main__":
    DIRECTORY = os.environ.get("CORPUS_DIR", "text_files")
    chunks = chunk_documents(DIRECTORY)

    # --- Report total chunk count (Milestone 3 checklist) ---
    print(f"\n{'#' * 70}")
    print(f"TOTAL CHUNKS: {len(chunks)}")
    lengths = [len(c.page_content) for c in chunks]
    if lengths:
        print(f"chunk length  min={min(lengths)}  max={max(lengths)}  avg={sum(lengths)//len(lengths)}")
    print(f"{'#' * 70}\n")

    # --- Print 5 representative chunks for inspection ---
    # Spread the sample across the corpus instead of clustering on one file.
    step = max(1, len(chunks) // 5)
    sample = chunks[::step][:5]
    for n, c in enumerate(sample, 1):
        print("=" * 70)
        print(f"SAMPLE {n}  |  source: {c.metadata['source']}  |  "
              f"chunk_index: {c.metadata['chunk_index']}  |  {len(c.page_content)} chars")
        print("-" * 70)
        print(c.page_content)
        print()