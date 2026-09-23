# Zenith Corp Policy Assistant — a document-grounded (RAG) chatbot

Employees ask questions in plain English; the bot answers **only** from Zenith Corp's policy
PDFs, cites the page numbers, and refuses when the answer isn't in the documents.

## Architecture

```
            OFFLINE (ingest.py, run once)                     ONLINE (rag.py, every question)
 ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌─────────┐      ┌──────────┐   ┌──────────────────┐
 │ 102-page │→ │ extract + │→ │ section- │→ │  embed  │→ DB  │ question │ → │ hybrid retrieval │
 │   PDF    │  │   clean   │  │ 900 char │  │ bge-sm  │      └──────────┘   │ FAISS+BM25, MMR  │
 └──────────┘  └───────────┘  │  aware   │  └─────────┘                     └────────┬─────────┘
                              │+page/sec │                                          ▼
                              └──────────┘                  relevance gate ── too low → "not found"
                                                                   │ ok
                                                                   ▼
                                                  strict prompt + top-8 chunks → LLM (temp 0)
                                                                   ▼
                                                     answer with [p. N] citations + sources
```

## Project files

| File | Role |
|---|---|
| `generate_policy_pdf.py` | Creates the 102-page sample handbook (`data/Zenith_Corp_Employee_Handbook.pdf`) |
| `ingest.py` | Load → clean → chunk → embed → save FAISS index |
| `rag.py` | Retrieval, guardrails, prompt, LLM call. Also a terminal chat (`python rag.py`) |
| `app.py` | Streamlit chat UI with a "Sources used" panel |
| `evaluate.py` | Retrieval hit-rate, answer accuracy, and refusal tests |
| `config.py` | All settings (chunk size, top-k, threshold, model) |

## How to run

```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # then add your LLM key
python generate_policy_pdf.py                         # PDF is already included; regenerate if you like
python ingest.py                                      # builds index/ (downloads the embedding model once)
python evaluate.py                                    # check retrieval + calibrate MIN_SIMILARITY
python evaluate.py --full                             # end-to-end, needs the LLM key
streamlit run app.py                                  # open http://localhost:8501
```

## Key design decisions

**Why RAG and not fine-tuning?** Policies change; with RAG you just re-run `ingest.py`. Fine-tuning
bakes facts into weights, can't cite sources and still hallucinates.

**Extraction — pdfplumber over pypdf.** pypdf split every table cell onto its own line, so
"Casual Leave (CL) 12 days" became disconnected fragments. pdfplumber keeps rows intact, which
matters because many policy facts live in tables. The repeating page footer is stripped so it
doesn't pollute every chunk.

**Chunking — section-aware, max 900 characters, 150 overlap.** The document is first cut at every
heading, and only sections longer than 900 characters are split further (on paragraph → line →
sentence → word boundaries, with overlap so a fact is never cut in half). The first version cut
blindly every 900 characters, which glued half of the Tier 1 allowance table, *without its column
headers*, to the Tier 2 table; the LLM then saw two different "G4" values and refused to answer.
Section-aware chunking keeps every table whole with its title and header row. 102 pages → 309 chunks.

**Contextual enrichment.** Some chapters open with a short intro that defines terms used later
(Annexure A: "Tier 1 - Mumbai, Delhi NCR, ..."). That intro is attached to every chunk in the
chapter, both for embedding and in the context shown to the LLM.

**Metadata — page, chapter, section on every chunk.** Enables citations, and the chapter/section
title is prepended to the text that gets embedded, so a chunk saying "12 days… credited on
1 January" is clearly *about leave* to the embedding model.

**Embeddings — `BAAI/bge-small-en-v1.5`.** Free, runs locally on CPU, strong on retrieval
benchmarks for its size (384-dim). Documents never leave the company for embedding.

**Hybrid retrieval — dense (FAISS) + keyword (BM25), merged with Reciprocal Rank Fusion.**
Dense search understands paraphrases ("time off" ≈ "leave"); BM25 nails exact tokens like
"ZEP", "FIN-02", "G4". RRF combines the two rankings without needing to normalise their scores.

**Diversity — Maximal Marginal Relevance (MMR, λ = 0.6).** From the top 30 fused candidates, the
final 8 are picked to be relevant *and* different from each other, so near-duplicate chunks
(e.g. many worked scenarios written from the same template) don't fill every slot.

**Grounding guardrails (the core business requirement).**
1. *Relevance gate*: if the best chunk's similarity is below `MIN_SIMILARITY`, the bot returns
   "not found" **without calling the LLM** — it gets no chance to use general knowledge.
2. *Strict system prompt*: answer only from context, refuse with a fixed message otherwise,
   quote numbers exactly, cite pages, ignore instructions inside documents (prompt-injection defence).
3. *Temperature 0* for deterministic, factual output. For reasoning models (gpt-oss) the bot uses
   low reasoning effort and retries automatically if a reply comes back empty.
4. *Citations + source panel* so employees can verify every answer.

**Follow-up questions.** Short follow-ups ("and for sick leave?") are combined with the previous
question before searching, and the last few turns are passed to the LLM.

## Evaluation

`evaluate.py` contains 26 employee questions with expected facts and 4 out-of-scope questions. It
reports retrieval hit-rate (is the answer in the top 8 chunks?), end-to-end answer accuracy, and
correct refusals, and prints similarity scores so the gate threshold is chosen from data.

Results (bge-small-en-v1.5 + Groq openai/gpt-oss-20b):

- Retrieval hit-rate: **25/26**, all 25 direct questions pass.
- Similarity gate: lowest in-scope score 0.66; off-topic questions 0.51–0.56, so `MIN_SIMILARITY = 0.60`.
- "What is Infosys's leave policy?" scores 0.67 and passes the gate because it shares the word
  *leave*; the strict prompt (second guardrail) correctly refuses it.
- The answer checker normalises Unicode, because gpt-oss writes non-breaking spaces
  ("26 weeks") that broke plain string matching and caused a false FAIL.

## Known limitation: multi-hop questions

"What is the hotel limit for a G4 employee in Mumbai?" needs two facts from different places:
Mumbai is a Tier 1 city (Annexure A intro) and the Tier 1 table gives G4 = INR 7,000. Diagnosis
showed the Tier 1 table ranked 8th on BM25 and 21st on dense search, while six near-identical
worked-scenario chunks ("Sneha (G4) to Indore", "Arjun (G3) to Mumbai", ...) took most of the top 8.
Section-aware chunking, contextual enrichment, a larger candidate pool and MMR (tested down to
λ = 0.4) improved the chunks but did not bring the table into the top 8 with bge-small. Asked
directly ("hotel limit for G4 in Tier 1 cities"), the bot answers correctly.

## Possible improvements

A cross-encoder re-ranker over the top 30 candidates, or LLM query rewriting that first resolves
"Mumbai" to "Tier 1" (both target the multi-hop limitation above); a larger embedding model; a persistent vector DB (Chroma/Qdrant) with
per-document access control; incremental re-indexing when a PDF changes; logging unanswered
questions so HR can see documentation gaps; streaming responses in the UI.
