
# Legal Audit Engine

A lightweight Python tool that scans contract documents and extracts critical terms like **termination clauses**, **liability caps**, and **data privacy compliance**.

Instead of reading through lengthy agreements line by line, this script uses Retrieval-Augmented Generation (RAG) to index your documents locally and query Google's Gemini models. It finds relevant clauses, evaluates them against standard legal norms, and flags potential gaps.

> **Note:** This tool is built for quick screening and educational purposes. It is **not** a substitute for actual legal counsel. Always have a qualified attorney review important contracts.


## Key Capabilities

**Multi-Format Ingestion:** Scans PDFs, DOCX files, plain text, and other formats supported by LlamaIndex straight from a local directory.
**Persistent Local Indexing:** Indexes your files once and caches the embeddings locally, making subsequent runs almost instant.
**Targeted Modular Audits:** Runs distinct, topic-focused evaluations for:
**Termination Terms:** Notice periods, cause vs. convenience, and cure windows.
**Liability & Indemnity:** Caps on damages, exclusions, and indemnification obligations.
**Data Privacy:** Compliance alignments (GDPR, India’s DPDP Act), security standards, and breach notifications.


**Automatic Failover:** Includes retry logic with fallback models in case the API hits rate limits or model deprecations.


## Tech Stack

**RAG Orchestration:** [LlamaIndex](https://www.llamaindex.ai/)
**LLM Engine:** Google Gemini (via `llama-index-llms-google-genai`)
**Embeddings:** Hugging Face `BAAI/bge-small-en-v1.5` (runs completely on your local machine)
**Config Management:** `python-dotenv`


## Project Layout

```
legal_audit_engine/
├── app.py              # Main execution script
├── documents/          # Input folder for target contracts (ignored by Git)
├── storage/            # Local vector index cache (ignored by Git)
├── .env                # Local API keys (ignored by Git)
├── .env.example        # Environment setup template
├── requirements.txt    # Project dependencies
└── README.md           # Documentation

```


## Getting Started

### 1. Clone the Repository

bash
git clone https://github.com/<your-username>/legal-audit-engine.git
cd legal-audit-engine


### 2. Set Up a Virtual Environment

bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate



### 3. Install Dependencies

bash
pip install -r requirements.txt



### 4. Configure Your API Key

1. Grab a free API key from [Google AI Studio](https://aistudio.google.com/).
2. Copy `.env.example` to `.env`.
3. Add your key:

env
GEMINI_API_KEY=your_gemini_api_key_here



### 5. Add Your Contracts

Create a `documents/` folder in the root directory and drop the target contracts inside.


## Running the Audit

bash
python app.py


On your first run, the tool will index all documents inside `documents/` and save the state to `./storage`. Detailed findings for each audit category will print directly to your console.

> **Tip:** If you add new contracts or modify existing files, simply delete the `./storage` directory so the tool rebuilds the vector index on the next run.


## Customization

* **Updating Models:** If Google retires a model version, update `MODEL_CANDIDATES` inside `app.py`.
* **Adjusting Search Depth:** Increase or decrease `similarity_top_k` in `app.py` (defaults to 6) depending on document length.
* **Custom Prompts:** Customize `AUDIT_TOPICS` in `app.py` to target specific clauses (e.g., non-compete clauses, IP rights, or payment terms).



## Practical Caveats

* **Search Limitations:** If a clause is marked as "Missing", it simply means it wasn't returned in the top retrieved chunks—always double-check the original document.
* **Contextual Accuracy:** AI outputs reflect general legal concepts, not jurisdiction-specific advice.
* **Data Security:** Avoid processing sensitive or confidential legal documents on unauthorized cloud services.


## What's Next

* [ ] Citation highlights showing exact page and paragraph numbers
* [ ] Automated export of audit summaries to Markdown and PDF reports
* [ ] Customizable compliance rulebooks per industry standard


## License

This project is licensed under the MIT License.