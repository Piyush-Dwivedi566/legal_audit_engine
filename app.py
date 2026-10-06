import os
import sys
import time
from dotenv import load_dotenv

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    StorageContext,
    load_index_from_storage,
)
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from google.genai.errors import APIError

# Suppress Hugging Face warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 1. Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file!")

# 2. Models to try, in order. If one is busy or unavailable, the next is used.
#    Edit this list using the names printed by client.models.list().
MODEL_CANDIDATES = [
    "models/gemini-3.8-flash",
    # "models/<flash-lite-model-from-your-list>",
]

Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

PERSIST_DIR = "./storage"

# 3. Load or create vector index
if os.path.exists(PERSIST_DIR):
    print("Loading existing vector index from local storage...")
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)
else:
    docs_dir = "./documents"
    if not os.path.exists(docs_dir) or not os.listdir(docs_dir):
        print(f"Error: Directory '{docs_dir}' is empty or missing.")
        sys.exit(1)

    print(f"Loading documents from '{docs_dir}'...")
    documents = SimpleDirectoryReader(docs_dir).load_data()

    print(f"Indexing {len(documents)} document sections locally...")
    index = VectorStoreIndex.from_documents(documents, show_progress=True)

    print(f"Saving index to '{PERSIST_DIR}' for faster future execution...")
    index.storage_context.persist(persist_dir=PERSIST_DIR)


# 4. Query helper with retry + model fallback
def run_audit_query(prompt, attempts_per_model=4):
    last_error = None
    for model_name in MODEL_CANDIDATES:
        llm = GoogleGenAI(model=model_name, api_key=api_key)
        engine = index.as_query_engine(llm=llm, similarity_top_k=6)

        for i in range(attempts_per_model):
            try:
                return engine.query(prompt)
            except APIError as e:
                last_error = e
                code = getattr(e, "code", None)

                # Model doesn't exist / not available -> skip to next model
                if code == 404:
                    print(f"[{model_name}] not available (404). Trying next model...")
                    break

                # Overloaded (503) or rate limited (429) -> wait and retry
                if code in (429, 500, 503):
                    wait = 5 * (2 ** i)  # 5s, 10s, 20s, 40s
                    print(f"[{model_name}] busy ({code}), attempt {i+1}/{attempts_per_model}. "
                          f"Retrying in {wait}s...")
                    time.sleep(wait)
                    continue

                # Anything else (bad key, bad request) -> don't retry
                raise

        else:
            print(f"[{model_name}] still busy. Trying next model...")

    raise RuntimeError(f"All models failed. Last error: {last_error}")


# 5. Run the audit, one focused query per topic
AUDIT_TOPICS = {
    "Termination Clauses": (
        "Find all termination clauses in the document: termination for cause, "
        "termination for convenience, notice periods, and cure periods. "
        "Quote the relevant wording and assess whether it meets standard "
        "legal compliance expectations. Flag anything missing or one-sided."
    ),
    "Liability Caps": (
        "Find all limitation of liability, liability cap, and indemnity provisions. "
        "Quote the relevant wording and assess whether they are reasonable and "
        "balanced under standard practice. Flag anything missing or unusual."
    ),
    "Data Privacy": (
        "Find all data protection and privacy terms: data handling, confidentiality, "
        "security obligations, breach notification, and any reference to laws such as "
        "GDPR or India's DPDP Act. Quote the relevant wording and assess compliance. "
        "Flag anything missing."
    ),
}

print("\nRunning compliance audit...\n")
print("=" * 60)
print("AUDIT RESULT")
print("=" * 60)

for title, prompt in AUDIT_TOPICS.items():
    print(f"\n--- {title} ---")
    result = run_audit_query(prompt)
    print(str(result))