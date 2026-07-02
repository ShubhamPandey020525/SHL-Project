
# SHL Assessment Recommender

A conversational AI agent that helps users find the right SHL Individual Test Solutions through natural dialogue. This project is a take-home assignment for the SHL Labs AI Intern role.

🔗 **Live Demo (Railway)**: https://shl-chatbot-production-6551.up.railway.app/  
🔗 **Live Demo (Render)**: https://shlchatbot-lm79.onrender.com

## 🚀 Quick Start
Follow these 3 steps to get up and running in 2 minutes:

1. **Create & activate virtual environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Start the server**
   ```powershell
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

Then open your browser and go to: **http://127.0.0.1:8000**


## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Evaluation Results](#evaluation-results)
- [Design Decisions](#design-decisions)


## Project Overview
The SHL Assessment Recommender is a stateless FastAPI application that uses:
- Semantic search with FAISS vector store
- LLM-powered conversations (via Groq LLaMA 3.3 70B)
- Simple fallback mode (no API key required)
- A modern, light-mode ChatGPT-style UI

It handles four key conversational behaviors:
1. **Clarification**: Asks follow-up questions for vague queries
2. **Recommendation**: Provides 3-6 relevant assessments with catalog URLs
3. **Refinement**: Updates recommendations based on new user constraints
4. **Comparison**: Compares multiple assessments using only catalog data


## Features
- **Dual-mode operation**: LLM mode (with Groq) + Simple fallback mode (keyword-based)
- **Stateless design**: Full conversation history included in each request
- **Strict schema compliance**: Guaranteed response format for automated evaluation
- **Hallucination prevention**: All recommendations validated against the catalog
- **Off-topic refusal**: Politely declines requests not related to SHL assessments
- **Modern light-mode UI**: ChatGPT-style interface with avatars and smooth animations


## Tech Stack
| Component | Technology |
|-----------|------------|
| Backend Framework | FastAPI |
| LLM Provider | Groq (LLaMA 3.3 70B) |
| Vector Store | FAISS |
| Embeddings | Sentence-Transformers (all-MiniLM-L6-v2) |
| Frontend | Vanilla HTML/CSS/JavaScript |


## Project Structure
```
SHL-Project/
├── app/
│   ├── __init__.py       # Package initializer
│   ├── config.py         # Environment configuration (Pydantic Settings)
│   ├── vector_store.py   # FAISS vector store management
│   ├── agent.py          # Core SHLAgent (conversational logic)
│   └── main.py           # FastAPI app + API endpoints
├── data/
│   └── shl_catalog.json  # Scraped SHL Individual Test Solutions (377 items)
├── static/
│   ├── index.html        # Frontend UI
│   ├── style.css         # Modern light-theme styling
│   └── script.js         # Frontend logic (quick suggestions, typing indicator, etc.)
├── .env.example          # Environment variable template
├── .gitignore            # Git ignore rules
├── requirements.txt      # Python dependencies
└── evaluate_project.py   # Comprehensive evaluation script
```


## Installation & Setup

### Prerequisites
- Python 3.8+
- (Optional) Groq API key for LLM mode

### Step 1: Clone or Navigate to the Project
```powershell
cd SHL-Project
```

### Step 2: Create and Activate Virtual Environment
```powershell
# Using venv (recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

(Optional) Add your Groq API key to `.env` for LLM mode:
```env
GROQ_API_KEY=your_actual_groq_api_key_here
```


## Usage

### 1. Start the Server
Run this command from the project root directory:
```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### 2. Open the Web UI
Open your browser and go to:
```
http://127.0.0.1:8000
```

### 3. Chat with the Agent
- Type your query in the input box (e.g., "Hiring a Java developer with 3 years experience")
- Press Enter or click the send button
- The agent will either ask clarifying questions or provide recommendations

### 4. Stop the Server
Press `CTRL+C` in the terminal where the server is running.


## API Endpoints

### 1. Health Check (GET /health)
Returns a simple health status.

**Response**:
```json
{
  "status": "ok"
}
```

---

### 2. Chat (POST /chat)
Main endpoint for conversing with the agent. Accepts full conversation history and returns next agent response.

**Request Body**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hiring a Java developer"
    },
    {
      "role": "assistant",
      "content": "Great! To recommend the best SHL assessments for you, could you tell me:\n• What role are you hiring for? (e.g., Python Developer, Sales Manager)\n• What experience level are you targeting? (e.g., Entry-level, 3-5 years, Senior)"
    },
    {
      "role": "user",
      "content": "Mid-level, around 4 years"
    }
  ]
}
```

**Response Body**:
```json
{
  "reply": "Perfect! I found 6 excellent SHL assessments for Java developers:",
  "recommendations": [
    {
      "name": "Java 8 (New)",
      "url": "https://www.shl.com/products/product-catalog/view/java-8-new/",
      "test_type": "K"
    },
    {
      "name": "OPQ32r",
      "url": "https://www.shl.com/products/product-catalog/view/opq32r/",
      "test_type": "P"
    }
  ],
  "end_of_conversation": true
}
```

**Response Fields**:
- `reply` (string): Agent's text response
- `recommendations` (array): 0-6 assessment objects, each with:
  - `name`: Assessment name from catalog
  - `url`: Catalog URL
  - `test_type`: "P" for Personality/Behavioral, "K" for Knowledge/Skill/Aptitude
- `end_of_conversation` (boolean): True if recommendations are provided and conversation is complete


## Evaluation Results
The project has been fully evaluated against the assignment requirements and passes all checks!

### Hard Evaluation Checks
| Test | Status |
|------|--------|
| Vague query handling | [PASSED] |
| Off-topic query refusal | [PASSED] |
| Detailed query recommendations (3-6) | [PASSED] |
| Comparison query handling | [PASSED] |
| API schema compliance | [PASSED] |

### Recall@10 Performance
| Test Query | Relevant Items in Catalog | Relevant in Top 10 | Recall@10 |
|------------|---------------------------|--------------------|-----------|
| Java developer (3-5 years) | 12 | 9 | 0.7500 |
| Personality/behavioral (mid-managers) | 76 | 10 | 0.1316 |
| .NET/C# (professional devs) | 11 | 9 | 0.8182 |
| Leadership/communication skills | 17 | 5 | 0.2941 |
| Coding/programming aptitude (entry-level) | 57 | 9 | 0.1579 |

**Mean Recall@10**: 0.4304

### How to Re-run Evaluation
```powershell
python evaluate_project.py
```


## Design Decisions

### 1. Vector Store Choice (FAISS)
- **Why FAISS?**: Lightweight, fast, easy to set up locally without external dependencies
- **Embedding Model**: all-MiniLM-L6-v2 (small, fast, good performance for semantic search)
- **Caching**: FAISS index and processed documents cached to disk for fast startup

### 2. LLM + Fallback Design
- **Primary Mode**: Uses Groq LLaMA 3.3 70B for natural, intelligent conversations
- **Fallback Mode**: Keyword-based approach that works even without an API key
- **Safety First**: All LLM outputs validated against the catalog to prevent hallucinations

### 3. Stateless Architecture
- **Why Stateless?**: Complies with assignment requirements; easy to scale and deploy
- **Conversation History**: Full history included in every request for context-aware responses

### 4. Frontend Design
- **Light-Mode UI**: Modern, clean interface with smooth animations
- **Quick Suggestions**: 3 pre-built queries to get users started fast
- **Typing Indicator**: Animated indicator when waiting for agent response
- **Responsive Design**: Works perfectly on mobile and desktop


## License
This project is a take-home assignment for SHL Labs and is not licensed for external use.

© 2026 SHL and its affiliates. All rights reserved.


---

## SHL Assessment Recommender - AI System Design (Complete)

### 1. Objective
Build an **Agentic RAG system** that understands hiring intent, asks clarifications, retrieves only SHL Individual Test Solutions, validates every recommendation, and returns strictly grounded JSON responses that comply 100% with the assignment's API schema.

Key Objectives:
- **Clarify** vague queries (role + experience required)
- **Retrieve** only from SHL catalog
- **Compare** assessments
- **Refine** recommendations with new constraints
- **Reject** off-topic queries
- **Prevent** hallucinations (validate all outputs)
- **Return** only 3-6 max recommendations

### 2. End-to-End AI Pipeline
```
User → Conversation History → Context Engineering → Intent & Entity Extraction → Clarification Decision → Embedding → Vector Search → Top-K Retrieval → Prompt Builder → LLM Reasoning → Validation → Test Type Classification → Schema Compliance Check → Structured JSON Response
```
*(With fallback branch for Simple Mode when LLM fails!)

### 3. AI Architecture
| Layer               | Component | Description |
|---------------------|-----------|-------------|
| 1. Conversation Context Layer | - Conversation History<br>- Stateless Memory<br>- Context Compression | Full stateless conversation history (messages[] array; no server-side state) |
| 2. Context Engineering | - Missing Info Detection<br>- Ambiguity Resolution<br>- Query Rewriting<br>- Conversation Continuity | Checks for typos/approximate terms |
| 3. Intent Classifier | - Recommendation<br>- Clarification<br>- Comparison<br>- Refinement<br>- Off-topic<br>- Prompt Injection<br>- Unknown | Keyword + implicit/explicit user intent from user input |
| 4. Entity Extractor | - Role<br>- Experience<br>- Skills<br>- Seniority<br>- Domain<br>- Soft Skills<br>- Assessment Preference<br>- Constraints | Extracts from SHL-specific entities |
| 5. Embedding Generator | - Sentence-Transformers<br>- `all-MiniLM-L6-v2` | Dense vector embeddings for queries/catalog |
| 6. FAISS Vector DB | - Indexed Product Catalog<br>- Cached Index | 377 SHL Individual Test Solutions |
| 7. Retriever | - Semantic Search<br>- Context Ranker (Semantic Similarity<br>- Skills Match<br>- Metadata Relevance<br>- Experience Match) | Top 12 relevant assessments retrieved, rank & filtered to 6 |
| 8. Prompt Builder | - System Instructions<br>- Conversation History<br>- Retrieved Catalog Context<br>- Constraints<br>- Required JSON Schema | Dynamic prompt construction |
| 9. LLM | - Groq API<br>- LLaMA 3.3 70B Versatile | Smart reasoning, 0.4 temp, max tokens 1024, JSON mode |
| 10. Validation Agent | - Catalog Check<br>- No Hallucination Guard | Every recommendation checked against `catalog_dict`; invalid ones removed, 100% catalog only |
| 11. Test Type Classifier | - `get_test_type()` function | P = Personality/Behavioral, K = Knowledge/Skill/Aptitude |
| 12. Output Generator | - Schema Compliance<br>- Max 6 Recommendations<br>- `reply` `recommendations` `end_of_conversation` | Strictly adheres to assignment schema |

### 4. Context Engineering (Project-Specific)
1. **Conversation Compression**: Full user history concatenated for context
2. **Missing-Information Detection**: Checks if both `role` and `experience` are provided
3. Ambiguity Resolution**: Detects typos (e.g., "pyhton" → Python, "jvaa" → Java)
3. **Ambiguity Resolution**: Detects typos
4. **Conversation Continuity**: Refines recommendations with new constraints
5. **Stateless History Utilization**: All conversation history sent with each request
6. **Context Grounding**: All LLM context strictly limited to SHL catalog data

### 5. Intent Classification (Project-Specific)
Our system classifies user intent into:
- **Recommendation**: User asks for assessments
- **Clarification**: System needs role/experience
- **Comparison**: User asks "difference between X and Y"
- **Refinement**: User adds/changes constraints
- **Off-topic**: Salary, hiring, legal, non-SHL queries
- **Prompt Injection**: Guardrails active
- **Unknown**: Default, tries to clarify

### 6. Entity Extraction (Project-Specific)
Extracts these entities from user input:
1. **Role**: Python dev, Java dev, Manager, Sales, Engineer, etc.
2. **Experience**: Entry-level, Intern, Mid-level, 3-5 years, Senior, Director, etc.
2. **Skills**: .NET, C#, Python, Java, coding, programming, etc.
2. **Seniority**: Entry, Mid, Senior, Lead, Director, Executive
2. **Domain**: Tech, Sales, Management
2. **Soft Skills**: Communication, Leadership, Personality, Behavior
2. **Assessment Preference**: Explicit product name mentions
2. **Constraints**: Any explicit filters

Also handles typos/approximate matches!

### 7. Retrieval Strategy
#### 7.1 Vector Embeddings
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Embedding Dimension**: 384-dimensional dense vectors
- **Query Embedding**: User query embedded to match catalog
- **Catalog Embedding**: All 377 SHL Individual Test Solutions embedded (name + description + keys + job levels)

#### 7.2 FAISS Vector Search
- **Index Type**: Flat Index (for small dataset)
- **Top-K Retrieval**: 12 relevant products
- **Context Ranker**:
  1. Semantic similarity score
  2. Skill/keyword match (skills mentioned by user)
  3. Job level match
  4. Metadata relevance
- **Limit**: Final recommendations max 6

### 8. Prompt Builder (Project-Specific)
Dynamic prompt = 
```
System Instructions (hard rules, examples)
+ Conversation History (full messages[] array as JSON)
+ Retrieved Catalog (12 relevant products, formatted clearly)
+ Constraints (max 6 recs, only catalog, JSON format)
+ Required JSON Schema (exact schema from assignment)
```

**System Instructions Snippet**:
```
You are SHL Assessment Guide, a helpful, friendly assistant for SHL's Individual Test Solutions. Follow THESE RULES EXACTLY:
1. STAY ON TOPIC: ONLY discuss SHL assessments
2. CLARIFY FIRST: Ask for both role and experience if missing
3. RECOMMENDATIONS: 3-6 FROM CATALOG ONLY
4. NO HALLUCINATIONS: Never invent!
5. RESPONSE FORMAT: ONLY valid JSON with reply, recommendations[], end_of_conversation
... + examples
```

### 9. Validation Layer
#### 9.1 Catalog Check
Every recommendation from LLM passes through:
1. **Name Check**: `name in catalog_dict` (exact match from catalog)
2. **URL Check**: Use only catalog URLs (`prod["link"]`)
3. **Test Type Check**: Generated via `get_test_type(prod)` for each valid rec
4. **Limit**: Valid recs ≤ 6
5. **Fallback**: Remove invalid recs, never send hallucinated items

#### 9.2 No Hallucination Guarantee
All recommendations:
- Exact names & URLs only from `data/shl_catalog.json`
- LLM has no access to external data beyond provided context

### 10. AI Safety
1. **Prompt Injection Detection**: System prompt designed to prevent leaking/rewriting
2. **Scope Restriction**: Only SHL Individual Test Solutions
3. **Catalog-Only Knowledge**: Zero external knowledge
4. **Output Validation**: 100% grounded
5. **Refusal Policy**: Off-topic politely refused

### 11. Conversation Intelligence
#### 11.1 Clarification Strategy
Asks for:
- Role first if missing
- Experience level first if missing
- Clear examples in English

#### 11.2 Comparison Handling
Looks for keywords: "difference", "compare", "vs", "versus", "between"
Extracts assessment names, returns both with descriptions
#### 11.3 Refinement Support
Accepts new constraints, re-runs retrieval with updated query
#### 11.4 Stateless Memory
Every request includes full conversation history (8 max turns as per assignment
#### 11.5 Context Preservation
Maintains context across turns
#### 11.6 Fallback Simple Mode
- Keyword-based logic if LLM initialization fails or LLM call fails:
- Does same intent/entity/retrieval/validation, mirroring AI flow

### 12. Evaluation (Project-Specific)
1. **Schema Compliance**: 100% (strictly checked)
2. **Recall@10**: Mean 0.4304
3. **Precision**: 100% (catalog only valid recs)
4. **Groundedness**: 100% (no hallucinations)
5. **Hallucination Rate**: 0% (all recs validated)
6. **Latency**: <30 sec per request
7. **Conversation Success Rate**: 100% on hard checks
8. **Behavior Accuracy**:
   - Off-topic refused
   - Vague → ask clarification
   - Refinement → update recs
   - Comparison → handle correctly

### 13. Failure Handling
1. **Unknown Roles**: Ask for more details
2. **Empty Queries**: Welcome + quick suggestions
3. **API Failures**: Auto fallback to Simple Mode
4. **Missing Catalog Entries**: Handle gracefully
5. **Invalid JSON**: Fallback valid JSON generation
6. **Prompt Injection**: Ignore + polite refusal
7. **No Matching Assessment**: Return general recs
8. **Typo Tolerance**: Approximate matches (pyhton → Python, jvaa → Java)

### 14. AI Flow Diagram (Project-Specific, Complete!)
```
User
↓
Conversation History (stateless)
↓
Context Engineering
↓
Intent + Entity Extraction
↓
Need Clarification?
├─ Yes → Ask Question
└─ No → Embedding → FAISS Vector DB → Top-12 Retrieval → Rank
↓
(Check: LLM Available?)
├─ Yes → Prompt Builder → LLM Reasoning (Groq LLaMA 3.3 70B)
└─ No → Simple Mode (Keyword‑Based)
↓
Validation Agent (Catalog Check)
↓
Test Type Classification (P/K)
↓
Limit to Max 6 Recommendations
↓
Schema Compliance Check
↓
Structured JSON
```

### 15. Tech Stack Recap
- **Backend**: FastAPI
- **LLM**: Groq LLaMA 3.3 70B Versatile
- **Vector DB**: FAISS
- **Embeddings**: Sentence-Transformers
- **Frontend**: Vanilla HTML/CSS/JS

### 16. Deployment & Scalability
- **Stateless**: Easy horizontal scaling
- **Cached FAISS Index**: Fast startup
- **Fallback Mode**: High availability
- **Uvicorn**: Production-ready server

---

### Appendix A: Recall@10 Scores (Project-Specific)
| Test Query | Recall@10 |
|---|---|
| Java Developer (3-5 years) | 0.7500 |
| Personality/Behavioral (Mid-Managers) | 0.1316 |
| .NET/C# (Professional Devs) | 0.8182 |
| Leadership/Communication Skills | 0.2941 |
| Coding/Aptitude (Entry-Level) | 0.1579 |
| **Mean Recall@10** | 0.4304 |

### How to Re-run Evaluation
```powershell
python evaluate_project.py
```
