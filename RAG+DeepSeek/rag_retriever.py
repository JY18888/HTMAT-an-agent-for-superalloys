"""rag_retriever.py — Lightweight hybrid retriever for the HTMAT superalloy knowledge graph.

Uses TF-IDF weighted keyword matching over KG JSONL entries.
No external embedding model required — suitable for offline deployment.
"""
import math
import json
import os
import re
from pathlib import Path

KG_DIR = Path(__file__).resolve().parent.parent / "Alloy_KG_Project" / "1_Data"

_documents = None
_vocab = None
_idf = None


def _load_kg():
    """Load all knowledge graph JSONL files and build a TF-IDF index."""
    global _documents, _vocab, _idf
    if _documents is not None:
        return

    _documents = []
    doc_freq = {}
    jsonl_files = sorted(Path(KG_DIR).glob("*.jsonl")) if KG_DIR.exists() else []

    if not jsonl_files:
        alt = Path(__file__).resolve().parent.parent / "Alloy_KG_Project" / "1_Data"
        jsonl_files = sorted(alt.glob("*.jsonl")) if alt.exists() else []

    for fpath in jsonl_files:
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                text = obj.get("text", "")
                if not text:
                    continue
                tokens = set(_tokenize(text))
                _documents.append({"id": obj.get("id", ""), "content": text, "tokens": tokens})
                for t in tokens:
                    doc_freq[t] = doc_freq.get(t, 0) + 1

    N = len(_documents)
    _idf = {t: math.log((N - freq + 0.5) / (freq + 0.5) + 1.0)
            for t, freq in doc_freq.items()}
    _vocab = set(doc_freq.keys())


def _tokenize(text):
    """Simple tokenizer: lowercase, split on non-alphanumeric, keep alphanumeric tokens."""
    text = text.lower()
    tokens = re.findall(r"[a-z0-9]+", text)
    chinese = re.findall(r"[一-鿿]+", text)
    return tokens + chinese


def search(query: str, k: int = 3):
    """Retrieve top-k KG entries matching the query.

    Args:
        query: Natural language query string.
        k: Number of results to return (default 3).

    Returns:
        List of dicts with keys 'id' and 'content'.
    """
    _load_kg()
    if not _documents:
        return []

    query_tokens = set(_tokenize(query))
    scores = []
    for doc in _documents:
        common = query_tokens & doc["tokens"]
        if not common:
            continue
        score = sum(_idf.get(t, 0) for t in common)
        scores.append((score, doc))

    scores.sort(key=lambda x: x[0], reverse=True)
    return [{"id": d["id"], "content": d["content"]} for _, d in scores[:k]]
