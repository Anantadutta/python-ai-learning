"""All tunable settings in one place. Override any of them with environment variables / .env."""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Paths
DATA_DIR = os.getenv("DATA_DIR", "data")                 # folder with the policy PDFs
INDEX_DIR = os.getenv("INDEX_DIR", "index")              # where the vector index is saved

# --- Chunking
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 900))           # characters per chunk
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 150))     # characters shared between neighbours

# --- Embeddings (runs locally, free)
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")
# bge models work best when the *query* (not the documents) gets this prefix
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

# --- Retrieval
TOP_K = int(os.getenv("TOP_K", 8))                       # chunks sent to the LLM
CANDIDATES = int(os.getenv("CANDIDATES", 30))            # chunks fetched by each retriever before fusion
MMR_LAMBDA = float(os.getenv("MMR_LAMBDA", 0.6))    # 1 = pure relevance, lower = more diverse chunks
MIN_SIMILARITY = float(os.getenv("MIN_SIMILARITY", 0.45))  # below this -> "not in the documents"

# --- LLM (any OpenAI-compatible API: OpenAI, Groq, Ollama, Gemini's OpenAI endpoint...)
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.0))  # 0 = no creativity, stick to facts
