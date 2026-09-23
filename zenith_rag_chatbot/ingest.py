"""
ingest.py  -  STEP 1 of the RAG pipeline (run once, or whenever the PDFs change)

    PDFs  ->  text per page  ->  clean  ->  chunks (with page + section metadata)
          ->  embeddings  ->  FAISS vector index  +  chunks.json  saved to disk

Run:  python ingest.py
"""
import glob
import json
import os
import re

import faiss
import numpy as np
import pdfplumber

import config

HEADING_RE = re.compile(r"^((?:\d+|S\d+|[A-K])\.\d+|[A-K] -|Q:)\s+.{3,90}$")
CHAPTER_RE = re.compile(r"^(Chapter \d+|Annexure [A-K]|Supplementary Policy S\d+) - .+$")
FOOTER_RE = re.compile(r"Zenith Corp - Employee Policy Handbook v2\.0 - Internal\s*Page \d+")


# ------------------------------------------------------------------ 1. load
def load_pdf(path):
    """Return a list of (page_number, text). Page numbers are 1-based, like a human reads them."""
    # pdfplumber keeps each table row on one line ("Casual Leave (CL) 12 days No No"),
    # which pypdf does not - important because many policy facts live in tables.
    pages = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append((i, clean(text)))
    return pages


# ------------------------------------------------------------------ 2. clean
def clean(text):
    text = FOOTER_RE.sub("", text)                  # repeated footer adds noise to every chunk
    text = re.sub(r"-\n(\w)", r"\1", text)           # re-join words hyphenated across lines
    text = re.sub(r"[ \t]+", " ", text)              # collapse runs of spaces
    text = re.sub(r"\n{3,}", "\n\n", text)           # collapse big gaps
    return text.strip()


# ------------------------------------------------------------------ 3. chunk
def split_text(text, size, overlap):
    """Recursive splitter: try to cut on paragraph breaks, then line breaks, then sentences,
    then spaces, so chunks end at natural boundaries instead of mid-word."""
    if len(text) <= size:
        return [text]
    for sep in ["\n\n", "\n", ". ", " "]:
        cut = text.rfind(sep, int(size * 0.5), size)
        if cut != -1:
            cut += len(sep)
            break
    else:
        cut = size
    head = text[:cut].strip()
    # step back by `overlap` chars (to a word boundary) so the next chunk shares some context
    back = max(cut - overlap, 1)
    space = text.rfind(" ", 0, back)
    nxt = space + 1 if space > cut * 0.5 else back
    return [head] + split_text(text[nxt:], size, overlap)


def chunk_document(pages, source):
    """Chunk the whole document (not page-by-page) so sections that cross a page break stay
    together. Each chunk remembers which page it started on and which section it belongs to."""
    full, page_starts = "", []
    for num, text in pages:
        page_starts.append((len(full), num))
        full += text + "\n\n"

    # remember where every chapter / section heading starts, for citations
    headings, offset = [], 0
    chapter = ""
    for line in full.split("\n"):
        s = line.strip()
        if CHAPTER_RE.match(s):
            chapter = s
        if CHAPTER_RE.match(s) or HEADING_RE.match(s):
            headings.append((offset, chapter, s))
        offset += len(line) + 1

    def page_of(pos):
        page = 1
        for start, num in page_starts:
            if start <= pos:
                page = num
        return page

    def section_of(pos):
        ch, sec = "", ""
        for start, c, s in headings:
            if start <= pos:
                ch, sec = c, s
        return ch, sec

    # SECTION-AWARE CHUNKING: first cut the document at every heading, then split only
    # sections that are too long. This keeps a table together with its title and header row.
    # (Cutting blindly every 900 chars once glued half of the "Tier 1" table to the "Tier 2"
    # table, so the LLM saw two different G4 hotel limits and couldn't tell which was which.)
    bounds = sorted({0, *[h[0] for h in headings], len(full)})
    sections = []
    for a, b in zip(bounds, bounds[1:]):
        text = full[a:b].strip()
        if not text:
            continue
        # merge tiny sections (a lone heading, a one-line note) into the previous one
        if sections and (len(text) < 250 or len(sections[-1][1]) < 250) \
                and len(sections[-1][1]) + len(text) <= config.CHUNK_SIZE:
            sections[-1] = (sections[-1][0], sections[-1][1] + "\n" + text)
        else:
            sections.append((a, text))

    pieces = []
    for start, text in sections:
        cursor = start
        for piece in split_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP):
            pos = full.find(piece[:60], cursor)
            pos = cursor if pos == -1 else pos
            cursor = pos
            pieces.append((pos, piece))

    # CONTEXTUAL ENRICHMENT: some chapters open with a short intro that defines terms used
    # later, e.g. Annexure A says "Tier 1 - Mumbai, Delhi NCR, ...", but the Tier 1 table
    # below never mentions Mumbai. We attach that intro to every chunk of the chapter, so
    # "hotel limit for G4 in Mumbai" can find (and answer from) the Tier 1 table chunk.
    intros = {}
    chapter_starts = [(o, s) for o, c, s in headings if s == c]
    for o, name in chapter_starts:
        nxt = [h[0] for h in headings if h[0] > o]
        body = full[o + len(name):nxt[0] if nxt else len(full)].strip()
        if 40 < len(body) <= 600:
            intros[name] = body

    chunks = []
    for pos, piece in pieces:
        chapter, section = section_of(pos)
        context = intros.get(chapter, "")
        if context and context[:80] in piece:      # this chunk IS the intro; don't repeat it
            context = ""
        # Prefixing the chapter name gives the embedding model context the raw chunk may lack
        # e.g. a chunk "12 days ... credited on 1 January" becomes clearly about LEAVE.
        chunks.append({
            "id": len(chunks),
            "source": os.path.basename(source),
            "page": page_of(pos),
            "chapter": chapter,
            "section": section,
            "text": piece,
            "context": context,
            "embed_text": "\n".join(x for x in [chapter, section, context, piece] if x),
        })
    return chunks


# ------------------------------------------------------------------ 4. embed + 5. index
def build_index(chunks):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(config.EMBED_MODEL)
    vectors = model.encode([c["embed_text"] for c in chunks], batch_size=32,
                           show_progress_bar=True, normalize_embeddings=True)
    vectors = np.asarray(vectors, dtype="float32")
    # Normalised vectors + inner product = cosine similarity
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    return index


def main():
    pdfs = sorted(glob.glob(os.path.join(config.DATA_DIR, "*.pdf")))
    if not pdfs:
        raise SystemExit(f"No PDFs in '{config.DATA_DIR}/'. Run generate_policy_pdf.py first.")

    all_chunks = []
    for path in pdfs:
        pages = load_pdf(path)
        chunks = chunk_document(pages, path)
        for c in chunks:                       # keep ids unique across multiple PDFs
            c["id"] = len(all_chunks)
            all_chunks.append(c)
        print(f"{os.path.basename(path)}: {len(pages)} pages -> {len(chunks)} chunks")

    print(f"Embedding {len(all_chunks)} chunks with {config.EMBED_MODEL} ...")
    index = build_index(all_chunks)

    os.makedirs(config.INDEX_DIR, exist_ok=True)
    faiss.write_index(index, os.path.join(config.INDEX_DIR, "faiss.index"))
    with open(os.path.join(config.INDEX_DIR, "chunks.json"), "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=1)
    print(f"Saved index to '{config.INDEX_DIR}/'")


if __name__ == "__main__":
    main()
