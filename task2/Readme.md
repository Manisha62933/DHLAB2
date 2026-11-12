# Task 2: Extraction of Indian Cultural Elements using RAG

Extracts Indian flora and fauna names from five historical texts using a local
RAG pipeline (PyMuPDF, sentence-transformers, FAISS, Ollama).

## Corpus
Tuzuk-i-Jahangiri, Mrigapakshishastra, Vrikshayurveda, Ain-i-Akbari, Gita Govinda
(English editions).

## Folder layout
```
task2_rag/
├── corpus_pdf/        <- put your PDFs here
├── corpus_txt/        <- created automatically
├── cache/             <- created automatically
├── rag_pipeline.py
├── flora_fauna.py     <- generated output (the deliverable)
├── results.json       <- generated: counts per text
└── requirements.txt
```

## Setup
1. Install Ollama from https://ollama.com and pull a model: `ollama pull llama3.1:8b`
2. `pip install -r requirements.txt`
3. Copy the PDFs into `corpus_pdf/`.

## Run
```
python rag_pipeline.py --limit 5     # quick test
python rag_pipeline.py               # full run (can take hours on CPU; safe to stop and resume)
```

## Pipeline
1. PDF to cleaned text
2. Chunk (350 words, 50 overlap)
3. Embed with all-MiniLM-L6-v2 and index with FAISS
4. Retrieve flora/fauna passages (top-k per query). Plant/animal treatises are scanned in full.
5. Extract names with a local LLM via Ollama (JSON output)
6. Verify each name appears in its source passage, remove generic words, merge plurals
7. Write `flora_fauna.py`