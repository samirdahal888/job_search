# Leapfrog Job Search - RAG Application

Intelligent job search using Retrieval-Augmented Generation (RAG) with hybrid vector search.

## Project Structure

```
leapfrog_job_search/
├── common/                      # Shared utilities and configurations
│   ├── __init__.py
│   ├── base_config.py          # Base configuration settings
│   ├── qdrant_config.py        # Qdrant-specific configuration
│   ├── exception.py            # Custom exceptions
│   ├── logger.py               # Logging utilities
│   └── utils.py                # Common utility functions
│
├── data_ingestion/             # Data loading and processing
│   ├── __init__.py
│   ├── config.py               # Data ingestion configuration
│   ├── artifacts/              # Data files
│   │   └── lf_job.csv         # Job listings data
│   ├── ingestion.py            # Data loading script
│   ├── create_chunks.py        # Text chunking utilities
│   ├── qdrant_client.py        # Qdrant client and operations
│   └── vector_database_setup.py # Database setup script
│
├── search/                     # Search functionality
│   ├── __init__.py
│   ├── config.py               # Search configuration
│   ├── routers/                # API endpoints
│   │   ├── __init__.py
│   │   └── search.py           # Search router
│   ├── schemas/                # Pydantic models
│   │   ├── __init__.py
│   │   └── search_schemas.py   # Request/response schemas
│   └── services/               # Business logic
│       ├── __init__.py
│       ├── search_service.py   # Main search orchestration
│       ├── query_parser.py     # Query parsing with LLM
│       ├── vector_search.py    # Vector search operations
│       └── llm_service.py      # LLM response generation
│
├── api_config.py               # API configuration
├── api_factory.py              # FastAPI app factory
├── main.py                     # Application entry point
├── pyproject.toml              # Project dependencies
└── README.md                   # This file
```

## Features

- **Hybrid Search**: Combines sparse (BM25) and dense (semantic) vector search
- **Natural Language Queries**: Parse user queries into semantic search + filters
- **AI-Powered Responses**: Generate natural language summaries using LLM
- **Advanced Filtering**: Filter by job level, category, company, location, and date
- **RESTful API**: FastAPI-based API with automatic documentation

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # or if using pyproject.toml
   pip install -e .
   ```

2. **Configure environment**:
   Create a `.env` file with:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   QDRANT_API_KEY=your_qdrant_api_key
   QDRANT_LOCATION=your_qdrant_url
   ```

3. **Setup vector database** (first time only):
   ```bash
   python -m data_ingestion.vector_database_setup
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## API Usage

Access the API at `http://localhost:8000`

**Search Endpoint**: `POST /api/query`

Example request:
```json
{
  "query": "Senior Python developer jobs in San Francisco",
  "top": 5
}
```

**API Documentation**: Visit `http://localhost:8000/docs` for interactive documentation

## Configuration

All configuration is managed through environment variables and config classes:

- **Base Config** (`common/base_config.py`): API keys, general settings
- **Qdrant Config** (`common/qdrant_config.py`): Vector search models
- **Data Ingestion Config** (`data_ingestion/config.py`): CSV path, chunking settings
- **Search Config** (`search/config.py`): Search-specific settings

## Architecture

### Feature-Based Organization

The project follows a feature-based folder structure where each module is self-contained:

1. **Common**: Shared functionality used across all modules
2. **Data Ingestion**: Handles data loading, cleaning, chunking, and vector DB setup
3. **Search**: Manages search queries, LLM processing, and response generation

### Key Components

- **Query Parser**: Uses LLM to extract semantic intent and filters from natural language
- **Vector Search**: Hybrid search combining sparse (BM25) and dense embeddings
- **LLM Service**: Generates human-friendly responses from search results
- **Search Service**: Orchestrates the entire search pipeline

## Development

Run in development mode with auto-reload:
```bash
python main.py
```

The server will start on `http://0.0.0.0:8000` by default.
