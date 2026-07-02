
# SHL Assessment Recommender

A conversational AI agent that helps users find the right SHL Individual Test Solutions through natural dialogue. This project is a take-home assignment for the SHL Labs AI Intern role.

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
