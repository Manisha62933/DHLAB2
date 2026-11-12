"""
=================================================================
Topic: RAG pipeline for extracting Indian flora and fauna names
=================================================================
Author Name(s): Manisha Low 
Short Description: End-to-end pipeline. Converts PDFs to text,
chunks them, embeds the chunks (sentence-transformers), indexes
them (FAISS), retrieves flora/fauna-related passages, and extracts
names with a LOCAL LLM through Ollama. Writes flora_fauna.py.
Semester: Monsoon Semester 2026
Affiliation:Student
=================================================================

Usage (run from the task2_rag folder):
    python rag_pipeline.py                      # full run
    python rag_pipeline.py --limit 5            # quick test: 5 chunks per text
    python rag_pipeline.py --model qwen2.5:7b   # use a different Ollama model
    python rag_pipeline.py --reconvert          # redo PDF -> text conversion
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import faiss
import fitz  # PyMuPDF
import numpy as np
import requests
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# ----------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------
BASE = Path(__file__).resolve().parent
PDF_DIR = BASE / "corpus_pdf"      # put your PDFs here
TXT_DIR = BASE / "corpus_txt"      # auto-created: cleaned text
CACHE_DIR = BASE / "cache"         # auto-created: saved LLM answers
OUT_PY = BASE / "flora_fauna.py"
OUT_JSON = BASE / "results.json"

CHUNK_WORDS = 350
CHUNK_OVERLAP = 50
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # English
DEFAULT_LLM = "llama3.1:8b"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Texts that are dense with plant/animal names are scanned in FULL
# (every chunk goes to the LLM). Matching is done on the lowercase
# PDF file name. Everything else uses retrieval (top-k chunks).
FULL_SCAN_KEYWORDS = ["mrigapakshi", "vriksha"]
FULL_SCAN_MAX_CHUNKS = 250   # small texts are scanned in full automatically
TOP_K = 30                   # chunks retrieved per query per text

FLORA_QUERIES = [
    "names of trees, plants, flowers, herbs and crops mentioned",
    "fruits, grains, vegetables and spices grown or eaten",
    "gardens, forests, groves and the trees growing in them",
    "medicinal plants, herbs and their uses",
]
FAUNA_QUERIES = [
    "names of animals, birds, fish, reptiles and insects mentioned",
    "hunting, elephants, horses, deer, tigers and other beasts",
    "birds such as peacocks, parrots, cranes and swans",
    "snakes, bees, fish and other creatures described",
]

# Generic words that are categories, not names
GENERIC = {
    "tree", "trees", "plant", "plants", "flower", "flowers", "herb", "herbs",
    "crop", "crops", "fruit", "fruits", "grass", "grasses", "forest", "garden",
    "animal", "animals", "beast", "beasts", "bird", "birds", "fish", "fishes",
    "insect", "insects", "reptile", "reptiles", "mammal", "mammals", "creature",
    "creatures", "cattle", "game", "wood", "seed", "seeds", "leaf", "leaves",
    "vegetable", "vegetables", "grain", "grains", "flora", "fauna", "wild animals",
}

PROMPT = """You are helping with a digital humanities project that studies plants and animals in historical Indian texts.

Read the passage and list the names of FLORA (plants, trees, flowers, herbs, crops, fruits, grasses) and FAUNA (animals, birds, fish, reptiles, insects) that are explicitly mentioned.

Rules:
- Only include specific names (for example "banyan", "peacock", "mango", "elephant"). Do NOT include general words such as "tree", "animal", "bird", "flowers".
- Copy each name exactly as it appears in the passage. Include Sanskrit, Persian or Hindi names if they appear (for example "hamsa", "asoka").
- Do not add anything that is not in the passage. Do not guess.
- If there are none, return empty lists.
- Respond with JSON only, in this exact shape: {"flora": [], "fauna": []}

Passage:
\"\"\"
<<CHUNK>>
\"\"\"
"""


# ----------------------------------------------------------------
# Step 1: PDF -> cleaned text
# ----------------------------------------------------------------
def clean_text(text: str) -> str:
    text = text.replace("\r", "")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)          # join hyphenated breaks
    text = re.sub(r"(?m)^\s*\d{1,4}\s*$", "", text)        # lone page numbers
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)           # single newline -> space
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def pdf_to_text(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    pages, empty = [], 0
    for page in doc:
        t = page.get_text()
        if len(t.strip()) < 20:
            empty += 1
        pages.append(t)
    if doc.page_count and empty / doc.page_count > 0.5:
        print(f"  WARNING: {pdf_path.name} looks scanned ({empty}/{doc.page_count} "
              f"pages have no text). You need OCR (Tesseract) for this file.")
    return clean_text("\n".join(pages))


def convert_all(reconvert: bool) -> list:
    PDF_DIR.mkdir(exist_ok=True)
    TXT_DIR.mkdir(exist_ok=True)
    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    if not pdfs:
        sys.exit(f"No PDFs found in {PDF_DIR}. Put your PDFs there and run again.")
    for pdf in pdfs:
        out = TXT_DIR / (pdf.stem + ".txt")
        if out.exists() and not reconvert:
            print(f"[skip] {pdf.name} already converted")
            continue
        print(f"[convert] {pdf.name}")
        out.write_text(pdf_to_text(pdf), encoding="utf-8")
    return sorted(TXT_DIR.glob("*.txt"))


# ----------------------------------------------------------------
# Step 2: chunk
# ----------------------------------------------------------------
def chunk_text(text: str) -> list:
    words = text.split()
    step = CHUNK_WORDS - CHUNK_OVERLAP
    chunks = []
    for i in range(0, len(words), step):
        piece = words[i:i + CHUNK_WORDS]
        if len(piece) >= 40 or not chunks:
            chunks.append(" ".join(piece))
        if i + CHUNK_WORDS >= len(words):
            break
    return chunks


# ----------------------------------------------------------------
# Step 3 and 4: embed, index, retrieve
# ----------------------------------------------------------------
def build_index(model, chunks):
    emb = model.encode(chunks, batch_size=32, normalize_embeddings=True,
                       show_progress_bar=True).astype("float32")
    index = faiss.IndexFlatIP(emb.shape[1])
    index.add(emb)
    return index


def retrieve_ids(model, index, n_chunks):
    ids = set()
    for q in FLORA_QUERIES + FAUNA_QUERIES:
        qv = model.encode([q], normalize_embeddings=True).astype("float32")
        _, found = index.search(qv, min(TOP_K, n_chunks))
        ids.update(int(i) for i in found[0] if i >= 0)
    return sorted(ids)


# ----------------------------------------------------------------
# Step 5: LLM extraction (Ollama)
# ----------------------------------------------------------------
def ask_llm(chunk: str, llm: str, retries: int = 3) -> dict:
    payload = {
        "model": llm,
        "prompt": PROMPT.replace("<<CHUNK>>", chunk),
        "stream": False,
        "format": "json",
        "options": {"temperature": 0, "num_ctx": 4096},
    }
    for attempt in range(retries):
        try:
            r = requests.post(OLLAMA_URL, json=payload, timeout=600)
            r.raise_for_status()
            data = json.loads(r.json()["response"])
            flora = [str(x) for x in data.get("flora", []) if isinstance(x, (str, int, float))]
            fauna = [str(x) for x in data.get("fauna", []) if isinstance(x, (str, int, float))]
            return {"flora": flora, "fauna": fauna}
        except requests.exceptions.ConnectionError:
            sys.exit("Cannot reach Ollama at localhost:11434. Start it (open the Ollama "
                     "app, or run `ollama serve`) and make sure the model is pulled: "
                     f"`ollama pull {llm}`")
        except (json.JSONDecodeError, KeyError, AttributeError):
            continue   # malformed output, retry
    return {"flora": [], "fauna": []}


# ----------------------------------------------------------------
# Step 6: verify and clean names
# ----------------------------------------------------------------
def verify(names: list, chunk_lower: str) -> list:
    """Keep only names that literally appear in the passage (anti-hallucination)."""
    kept = []
    for n in names:
        base = n.lower().strip()
        variants = {base, base.rstrip("s"), base + "s", base + "es"}
        if base and any(v and v in chunk_lower for v in variants):
            kept.append(n)
    return kept


def normalise(name: str):
    n = re.sub(r"^[^\w]+|[^\w]+$", "", name.lower().strip())
    n = re.sub(r"^(the|a|an)\s+", "", n)
    n = re.sub(r"\s+", " ", n)
    if len(n) < 3 or len(n) > 40 or re.search(r"\d", n) or len(n.split()) > 4:
        return None
    if n in GENERIC:
        return None
    return n


def merge_plurals(counts: dict) -> dict:
    merged = defaultdict(lambda: defaultdict(int))
    for name, by_src in counts.items():
        target = name
        for suffix in ("s", "es"):
            if name.endswith(suffix) and name[: -len(suffix)] in counts:
                target = name[: -len(suffix)]
        for src, c in by_src.items():
            merged[target][src] += c
    return merged


# ----------------------------------------------------------------
# Output
# ----------------------------------------------------------------
HEADER = '''"""
=================================================
===========
Topic: Extraction of Indian Cultural Elements
Using RAG
=================================================
===========
Author Name(s): Devroop Dasgupta
Short Description: Names of Indian flora and fauna extracted from
five historical texts (Tuzuk-i-Jahangiri, Mrigapakshishastra,
Vrikshayurveda, Ain-i-Akbari, Gita Govinda) using a RAG pipeline:
chunking, sentence-transformer embeddings, FAISS retrieval, and
extraction with a local LLM (Ollama). Every name was checked to
appear in the source passage. Counts and sources are in
results.json.
Semester: Monsoon Semester 2026
Affiliation: Department of Computer Science and Engineering,
Sir M. Visvesvaraya Institute of Technology, Bengaluru
=================================================
===========
"""
'''


def write_outputs(flora, fauna, llm):
    flora_names = sorted(flora)
    fauna_names = sorted(fauna)
    res = {
        "llm": llm,
        "embedding_model": EMBED_MODEL,
        "flora": {n.capitalize(): dict(flora[n]) for n in flora_names},
        "fauna": {n.capitalize(): dict(fauna[n]) for n in fauna_names},
    }
    OUT_JSON.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")

    def src_map(d):
        return {n.capitalize(): sorted(d[n].keys()) for n in sorted(d)}

    body = HEADER
    body += "\nflora_RAG_extraction = " + json.dumps(
        [n.capitalize() for n in flora_names], indent=4, ensure_ascii=False) + "\n"
    body += "\nfauna_RAG_extraction = " + json.dumps(
        [n.capitalize() for n in fauna_names], indent=4, ensure_ascii=False) + "\n"
    body += "\n# Which text(s) each name was found in\n"
    body += "flora_sources = " + json.dumps(src_map(flora), indent=4, ensure_ascii=False) + "\n"
    body += "\nfauna_sources = " + json.dumps(src_map(fauna), indent=4, ensure_ascii=False) + "\n"
    OUT_PY.write_text(body, encoding="utf-8")
    print(f"\nWrote {OUT_PY.name} ({len(flora_names)} flora, {len(fauna_names)} fauna) "
          f"and {OUT_JSON.name}")


# ----------------------------------------------------------------
# Main
# ----------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=DEFAULT_LLM, help="Ollama model name")
    ap.add_argument("--limit", type=int, default=0, help="max chunks per text (testing)")
    ap.add_argument("--reconvert", action="store_true", help="redo PDF conversion")
    args = ap.parse_args()

    CACHE_DIR.mkdir(exist_ok=True)
    txt_files = convert_all(args.reconvert)

    print(f"\nLoading embedding model: {EMBED_MODEL}")
    embedder = SentenceTransformer(EMBED_MODEL)

    flora_counts = defaultdict(lambda: defaultdict(int))
    fauna_counts = defaultdict(lambda: defaultdict(int))
    safe_model = re.sub(r"[^\w.-]", "_", args.model)

    for txt in txt_files:
        source = txt.stem
        chunks = chunk_text(txt.read_text(encoding="utf-8"))
        print(f"\n=== {source}: {len(chunks)} chunks ===")
        if not chunks:
            continue

        full = (any(k in source.lower() for k in FULL_SCAN_KEYWORDS)
                or len(chunks) <= FULL_SCAN_MAX_CHUNKS)
        if full:
            ids = list(range(len(chunks)))
            print("Mode: FULL scan (every chunk)")
        else:
            index = build_index(embedder, chunks)
            ids = retrieve_ids(embedder, index, len(chunks))
            print(f"Mode: RETRIEVAL ({len(ids)} chunks selected)")
        if args.limit:
            ids = ids[: args.limit]

        cache_file = CACHE_DIR / f"{source}__{safe_model}.json"
        cache = json.loads(cache_file.read_text(encoding="utf-8")) if cache_file.exists() else {}

        for n_done, i in enumerate(tqdm(ids, desc=source[:30]), start=1):
            key = str(i)
            if key not in cache:
                cache[key] = ask_llm(chunks[i], args.model)
                if n_done % 10 == 0:
                    cache_file.write_text(json.dumps(cache), encoding="utf-8")
            low = chunks[i].lower()
            for raw in verify(cache[key]["flora"], low):
                n = normalise(raw)
                if n:
                    flora_counts[n][source] += 1
            for raw in verify(cache[key]["fauna"], low):
                n = normalise(raw)
                if n:
                    fauna_counts[n][source] += 1
        cache_file.write_text(json.dumps(cache), encoding="utf-8")

    write_outputs(merge_plurals(flora_counts), merge_plurals(fauna_counts), args.model)


if __name__ == "__main__":
    main()