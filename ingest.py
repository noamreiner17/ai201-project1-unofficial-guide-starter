
import os
import re
import html
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Spec values from planning.md (Chunking Strategy section) 
CHUNK_SIZE = 600
CHUNK_OVERLAP = 150
CORPUS_DIR = "text_files"

# Official sources from planning.md Documents table. These are fetched once and
# cached as .txt in CORPUS_DIR on later runs they're already on disk and skipped. Also used in Query.py for source attribution,
OFFICIAL_SOURCES = {
    "OFFICIAL_Massell_Quad.txt":
        "https://www.brandeis.edu/dcl/housing-on-campus/residence-halls/massell.html",
    "OFFICIAL_North_Quad.txt":
        "https://www.brandeis.edu/dcl/housing-on-campus/residence-halls/north.html",
    "OFFICIAL_East_Quad.txt":
        "https://www.brandeis.edu/dcl/housing-on-campus/residence-halls/east.html",
    "OFFICIAL_New_FirstYear_Housing.txt":
        "https://www.brandeis.edu/dcl/housing-on-campus/new-first-year/index.html",
    "HOOT_East_Quad_Demolition.txt":
        "https://brandeishoot.com/brandeis-considering-demolition-of-east-quad-following-completion-of-new-residence-hall/",
}



def fetch_official_sources(directory_path=CORPUS_DIR):
    """
    Download the official Brandeis pages listed in planning.md, clean the HTML,
    and cache each as a .txt in directory_path. Files already on disk are skipped,
    so this only hits the network the first time (keeps later runs fast + reproducible).

    Requires: pip install requests beautifulsoup4
    Fails soft: if a fetch errors (offline, page moved), it prints a warning and
    continues with whatever local files exist.
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("[fetch] skipped — install with: pip install requests beautifulsoup4")
        return

    os.makedirs(directory_path, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0 (educational RAG project)"}

    for fname, url in OFFICIAL_SOURCES.items():
        path = os.path.join(directory_path, fname)
        if os.path.exists(path):
            continue  # already cached — don't re-scrape
        try:
            r = requests.get(url, headers=headers, timeout=20)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            # Drop non-content elements (nav, header, footer, scripts, etc.)
            for tag in soup(["nav", "header", "footer", "script", "style",
                             "aside", "form", "button"]):
                tag.decompose()
            main = soup.find("main") or soup.find("article") or soup.body or soup
            text = html.unescape(main.get_text(separator="\n"))
            # Keep substantive lines, drop short menu-ish fragments.
            lines = [ln.strip() for ln in text.split("\n")]
            lines = [ln for ln in lines if len(ln) > 40 or ln.endswith((".", "!", "?"))]
            text = re.sub(r"\n{3,}", "\n\n", "\n\n".join(lines)).strip()
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            flag = "  <-- short, inspect!" if len(text) < 200 else ""
            print(f"[fetch] saved {fname} ({len(text)} chars){flag}")
        except Exception as e:
            print(f"[fetch] failed {fname}: {e}")



def load_documents(directory_path: str):
    """Load every .txt file from disk as raw text. Returns list of {source, raw}."""
    raw_docs = []
    for fname in sorted(os.listdir(directory_path)):
        if not fname.lower().endswith(".txt"):
            continue
        with open(os.path.join(directory_path, fname), "r", encoding="utf-8") as f:
            raw_docs.append({"source": fname, "raw": f.read()})
    return raw_docs


def clean_text(raw: str) -> str:
    """
    Clean a raw document into substantive content ready for chunking.
    """
    text = re.sub(r"<[^>]+>", "", raw)                                  # strip tags
    text = html.unescape(text)                                          # decode entities
    text = re.sub(r"(?im)^\s*student\s+(comment|question)\s*:\s*", "", text)  # boilerplate
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
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


def chunk_documents(directory_path=CORPUS_DIR, fetch=True):
    """
    Full pass: (optionally fetch official) -> load -> clean -> chunk -> attach metadata.
    Returns: list[Document] with metadata {"source", "chunk_index"}.

    fetch=True caches the official Brandeis pages on first run. Set fetch=False to
    work purely offline from whatever .txt files already exist in directory_path.
    """
    if fetch:
        fetch_official_sources(directory_path)

    cleaned = clean_documents(load_documents(directory_path))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],  # paragraph -> line -> sentence -> word -> char
        length_function=len,
    )

    all_chunks = []
    for d in cleaned:
        for i, piece in enumerate(splitter.split_text(d["text"])):
            if not piece.strip():
                continue
            all_chunks.append(
                Document(page_content=piece,
                         metadata={"source": d["source"], "chunk_index": i})
            )
    return all_chunks

#sample test run to inspect the chunking output
if __name__ == "__main__":
    chunks = chunk_documents()

    print(f"\n{'#' * 70}")
    print(f"TOTAL CHUNKS: {len(chunks)}")
    lengths = [len(c.page_content) for c in chunks]
    if lengths:
        print(f"chunk length  min={min(lengths)}  max={max(lengths)}  avg={sum(lengths)//len(lengths)}")
    print(f"{'#' * 70}\n")

    step = max(1, len(chunks) // 5)
    for n, c in enumerate(chunks[::step][:5], 1):
        print("=" * 70)
        print(f"SAMPLE {n}  |  source: {c.metadata['source']}  |  "
              f"chunk_index: {c.metadata['chunk_index']}  |  {len(c.page_content)} chars")
        print("-" * 70)
        print(c.page_content)
        print()