# 🔍 Intelligent Job Search System

> **AI-Powered Job Search with Natural Language Understanding**

An advanced Retrieval-Augmented Generation (RAG) system that allows users to search for jobs using natural language queries and receive intelligent, context-aware responses. Built with FastAPI, Qdrant Vector Database, and Google Gemini AI.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Technology Stack](#-technology-stack)
- [Installation & Setup](#-installation--setup)
- [Usage Guide](#-usage-guide)
- [API Documentation](#-api-documentation)
- [Engineering Decisions](#-engineering-decisions)
- [Future Enhancements](#-future-enhancements)

## 🎯 Overview

This project implements a sophisticated job search system that understands natural language queries and returns relevant job listings with AI-generated summaries. Instead of traditional keyword matching, users can ask questions like:

- *"Find me senior Python developer jobs in San Francisco"*
- *"Show recent data science positions "*
- *"Entry level frontend jobs posted in the last 1 years"*

The system intelligently:
1. **Parses** the query to extract search intent and filters
2. **Searches** using hybrid vector search (combining semantic and keyword matching)
3. **Ranks** results using Reciprocal Rank Fusion (RRF)
4. **Generates** natural language summaries using Google Gemini AI

### 📊 Dataset

- **Source**: LeapFrog Jobs Dataset
- **Total Jobs**: 1,000 job listings
- **Companies**: 145 unique companies
- **Categories**: 7 job categories
- **Features**: Job title, company, location, level, category, description, publication date

## ✨ Key Features

### 🔍 Hybrid Search
Combines two search approaches for superior accuracy:
- **Sparse Vector (BM25)**: Traditional keyword-based search for exact matches
- **Dense Vector (Semantic)**: AI-powered semantic understanding using `sentence-transformers/all-MiniLM-L6-v2`
- **Fusion**: Reciprocal Rank Fusion (RRF) merges both results

### 🧠 AI-Powered Intelligence
- **Query Understanding**: LLM parses natural language into structured queries
- **Smart Filtering**: Automatically extracts filters (location, level, company, date)
- **Natural Responses**: Generates human-friendly summaries of search results

### 🎯 Advanced Filtering
Filter jobs by:
- **Job Level**: Senior, Mid, Entry Level, Internship
- **Category**: Software Engineering, Data Analytics, Design, Sales, etc.
- **Location**: City, region, or country
- **Company**: Specific company names
- **Date Range**: Recent jobs, last week, last month, etc.

### 🏗️ Production-Ready Architecture
- **Feature-Based Structure**: Modular organization (common, data_ingestion, search)
- **Exception Handling**: Comprehensive error handling with custom exceptions
- **Dependency Injection**: Clean, testable code with DI patterns
- **Type Safety**: Full type annotations throughout the codebase
- **Logging**: Structured logging for debugging and monitoring

## 🛠️ Technology Stack

### Backend Framework
- **FastAPI**: Modern, high-performance web framework
- **Uvicorn**: ASGI server for production deployment
- **Pydantic**: Data validation and settings management

### AI & Machine Learning
- **Google Gemini 2.5 Flash**: LLM for query parsing and response generation
- **Sentence Transformers**: `all-MiniLM-L6-v2` for semantic embeddings
- **BM25**: Sparse vector search for keyword matching

### Vector Database
- **Qdrant**: High-performance vector database
- **Hybrid Search**: Sparse + Dense vectors with RRF fusion
- **FastEmbed**: Built-in embedding models

### Data Processing
- **Pandas**: Data manipulation and analysis
- **BeautifulSoup**: HTML cleaning from job descriptions
- **LangChain Text Splitters**: Intelligent text chunking

### Development Tools
- **Python 3.12+**: Latest Python features
- **Type Hints**: Full type safety
- **Logging**: Structured logging with colored output

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.12+**
- **Qdrant Account** (or local Qdrant instance)
- **Google Gemini API Key**

### Step 1: Clone the Repository

```bash
git clone https://github.com/samirdahal888/leapfrog_job_search.git
cd leapfrog_job_search
```

### Step 2: Create Virtual Environment

```bash
python -m venv .venv

# Activate on Linux/Mac
source .venv/bin/activate

# Activate on Windows
.venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -e .
```

Or if you have `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```env
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Qdrant Configuration
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_LOCATION=https://your-cluster-url.qdrant.io

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_TO_CONSOLE=true
LOG_TO_FILE=false
```

### Step 5: Initialize Vector Database

**⚠️ Run this only once to set up the database:**

```bash
python -m data_ingestion.vector_database_setup
```

This will:
1. Load the job dataset from `data_ingestion/artifacts/lf_job.csv`
2. Clean HTML tags from job descriptions
3. Create text chunks with metadata
4. Generate embeddings (sparse + dense)
5. Upload to Qdrant vector database
6. Create field indexes for filtering

**Expected output:**
```
INFO: Successfully connected to Qdrant
INFO: Creating new collection: lf_jobs
INFO: Processing 1000 job records...
INFO: Created 1000 chunks with metadata
INFO: Starting upload of 1000 chunks in batch of 50
INFO: Uploaded batch 20/20 (50 chunks)
INFO: Successfully uploaded all 1000 chunks to Qdrant
INFO: Creating field indexes...
INFO: Vector database setup complete!
```

### Step 6: Run the Application

```bash
python main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redocs

## 📖 Usage Guide

### Making API Requests

#### Basic Search

```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python developer jobs",
    "top": 5
  }'
```

#### Advanced Search with Filters

```bash
# Search with location filter
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Senior data scientist in San Francisco",
    "top": 3
  }'

# Search with company filter
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Software engineer at Google",
    "top": 5
  }'

# Search with date filter
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Recent machine learning jobs posted in last 7 days",
    "top": 10
  }'
```

### Example Request & Response

**Request:**
```json
{
  "query": "Senior Python developer jobs in California",
  "top": 3
}
```

**Response:**
```json
{
  "success": true,
  "query": "Senior Python developer jobs in California",
  "response": "I found 3 senior Python developer positions in California. Top opportunities include a Senior Backend Engineer at Airbnb in San Francisco, a Senior Python Developer at Netflix in Los Gatos, and a Lead Software Engineer position at Google in Mountain View. All positions require 5+ years of Python experience and offer competitive compensation packages.",
  "jobs": [
    {
      "rank": 1,
      "score": 0.8945,
      "job_title": "Senior Backend Engineer",
      "company": "Airbnb",
      "category": "Software Engineering",
      "location": "San Francisco, CA",
      "job_level": "Senior Level",
      "job_id": "LF0123",
      "publication_date": "2024-11-15T10:30:00Z",
      "description_snippet": "We're looking for an experienced Python developer to join our backend team..."
    },
    {
      "rank": 2,
      "score": 0.8721,
      "job_title": "Senior Python Developer",
      "company": "Netflix",
      "category": "Software Engineering",
      "location": "Los Gatos, CA",
      "job_level": "Senior Level",
      "job_id": "LF0456",
      "publication_date": "2024-11-18T14:20:00Z",
      "description_snippet": "Join our data platform team to build scalable microservices..."
    },
    {
      "rank": 3,
      "score": 0.8534,
      "job_title": "Lead Software Engineer",
      "company": "Google",
      "category": "Software Engineering",
      "location": "Mountain View, CA",
      "job_level": "Senior Level",
      "job_id": "LF0789",
      "publication_date": "2024-11-10T09:15:00Z",
      "description_snippet": "Lead the development of our cloud infrastructure using Python and Go..."
    }
  ],
  "timestamp": "2024-11-23T15:45:30.123456"
}
```

### Query Examples

Here are some natural language queries the system understands:

| Query | What It Does |
|-------|-------------|
| `"Python jobs"` | Finds all Python-related positions |
| `"Senior data scientist at Google"` | Filters by level, role, and company |
| `"Frontend jobs in New York"` | Filters by category and location |
| `"Entry level positions"` | Filters by experience level |
| `"Recent marketing jobs"` | Shows jobs posted in last 7 days |
| `"ML engineer jobs posted last month"` | Filters by role and date range |
| `"Remote software engineer positions"` | Searches for remote opportunities |

## 📚 API Documentation

### Endpoint: `POST /api/query`

Search for jobs using natural language queries.

#### Request Body

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | ✅ Yes | - | Natural language search query |
| `top` | integer | ❌ No | 3 | Number of results to return (1-20) |

#### Response Schema

```typescript
{
  success: boolean,           // Request status
  query: string,             // Original query
  response: string,          // AI-generated summary
  jobs: [                    // Array of job results
    {
      rank: number,          // Result ranking (1, 2, 3...)
      score: number,         // Relevance score (0-1)
      job_title: string,     // Job title
      company: string,       // Company name
      category: string,      // Job category
      location: string,      // Job location
      job_level: string,     // Experience level
      job_id: string,        // Unique job identifier
      publication_date: string,  // ISO 8601 date
      description_snippet: string  // Job description preview
    }
  ],
  timestamp: string          // Response timestamp
}
```

#### Status Codes

| Code | Description |
|------|-------------|
| `200` | Successful search |
| `400` | Invalid query (empty, too short) |
| `404` | No results found |
| `422` | Validation error |
| `500` | Server error |
| `503` | Vector database or LLM unavailable |

### Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
  - Try out API calls directly from browser
  - See request/response schemas
  - Test different queries

- **ReDoc**: http://localhost:8000/redocs
  - Alternative documentation view
  - Clean, readable format

## 🧠 Engineering Decisions

### 1. Hybrid Search Strategy

**Decision**: Combine sparse (BM25) and dense (semantic) vectors with Reciprocal Rank Fusion

**Reasoning**:
- **Sparse vectors** excel at exact keyword matching (e.g., "Python", "AWS")
- **Dense vectors** understand semantic meaning (e.g., "ML" ≈ "Machine Learning")
- **RRF fusion** merges both approaches, leveraging strengths of each
- **Result**: Better accuracy than either approach alone

**Implementation**:
```python
# Prefetch from both search methods
prefetch=[
    Prefetch(query=Document(text=query, model="bm25"), using="sparse", limit=20),
    Prefetch(query=Document(text=query, model="sentence-transformers"), using="dense", limit=20)
]
# Fuse using RRF
query=FusionQuery(fusion=Fusion.RRF)
```

### 2. LLM-Powered Query Parsing

**Decision**: Use Google Gemini to parse natural language queries into structured filters

**Reasoning**:
- Users can ask questions naturally instead of learning query syntax
- LLM understands context (e.g., "Bay Area" → "San Francisco")
- Automatically extracts filters (location, level, company, date)
- Graceful degradation: if parsing fails, use original query

**Example Transformation**:
```
Input:  "Senior Python jobs at Google posted last week"
Output: {
  "semantic_query": "Python developer",
  "filters": {
    "Level": "Senior Level",
    "company": "Google",
    "category": "Software Engineering",
    "date_range": { "days": 7 }
  }
}
```

### 3. Feature-Based Architecture

**Decision**: Organize code by feature (common, data_ingestion, search) instead of type (models, views, controllers)

**Reasoning**:
- **Better modularity**: Each feature is self-contained
- **Easier to maintain**: Changes to search don't affect data ingestion
- **Scalable**: Easy to add new features (e.g., user module, recommendations)
- **Clear boundaries**: Each module has its own config, services, schemas

### 4. Comprehensive Exception Handling

**Decision**: Custom exception hierarchy with HTTP status codes and fallback mechanisms

**Reasoning**:
- **User-friendly errors**: Meaningful error messages
- **Graceful degradation**: Fallback responses when LLM fails
- **Proper HTTP codes**: 400 for bad input, 503 for service unavailable
- **Debugging**: Detailed logging for troubleshooting

**Exception Hierarchy**:
```
JobSearchError (base, 500)
├── VectorDatabaseError (503)
├── LLMError (503)
├── InvalidQueryError (400)
├── SearchError (500)
└── NoResultsError (404)
```

### 5. Dependency Injection Pattern

**Decision**: Use dependency injection for services and configurations

**Reasoning**:
- **Testability**: Easy to mock dependencies in tests
- **Flexibility**: Swap implementations without changing code
- **Clean code**: No global state or singletons
- **Type safety**: Full type hints for better IDE support

**Example**:
```python
def get_search_service() -> SearchService:
    return SearchService()

@router.post("/query")
def job_query(
    request: QueryRequest,
    service: SearchService = Depends(get_search_service)
):
    return service.search_jobs(request.query, request.top)
```

### 6. Text Chunking Strategy

**Decision**: Use LangChain's RecursiveCharacterTextSplitter with 1000 char chunks

**Reasoning**:
- **Balance**: Large enough for context, small enough for precise retrieval
- **Overlap**: 200 char overlap prevents information loss at boundaries
- **Metadata preservation**: Each chunk maintains job metadata (title, company, etc.)
- **Better embeddings**: Focused chunks produce more accurate embeddings

## 🔮 Future Enhancements

### Short-Term Improvements

1. **Reranker Model**
   - Add cross-encoder reranking for top results
   - Improves final ranking accuracy
   - Use models like `cross-encoder/ms-marco-MiniLM-L-6-v2`

2. **Caching Layer**
   - Redis cache for frequent queries
   - Reduce LLM API calls
   - Faster response times

3. **User Feedback Loop**
   - Allow users to rate results
   - Improve search quality over time
   - A/B testing for algorithm changes

4. **Batch Processing**
   - Support multiple queries in single request
   - Parallel processing for better throughput

### Long-Term Roadmap

1. **User Profiles & Personalization**
   - Save user preferences
   - Personalized job recommendations
   - Job alerts for matching positions

2. **Advanced Analytics**
   - Job market trends
   - Salary insights
   - Skills demand analysis
   - Company hiring patterns

3. **Multi-Language Support**
   - Support queries in multiple languages
   - Translate job descriptions
   - Cross-language semantic search

4. **Real-Time Data Pipeline**
   - Automated job scraping
   - Continuous database updates
   - Change detection and notifications

5. **Enhanced Filtering**
   - Salary range filters
   - Work type (remote, hybrid, onsite)
   - Benefits and perks
   - Company size and industry

6. **Application Tracking**
   - Track application status
   - Interview scheduling
   - Follow-up reminders

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Samir Dahal**
- GitHub: [@samirdahal888](https://github.com/samirdahal888)

## 🙏 Acknowledgments

- LeapFrog Technology for the job dataset
- Qdrant team for the excellent vector database
- Google for the Gemini API
- FastAPI community for the amazing framework

## 📞 Support

If you have questions or need help:
- 📧 Open an issue on GitHub
- 💬 Start a discussion in the repository

---

**Made with ❤️ for better job searching**
