"""Query parsing and filter extraction using LLM"""

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import google.generativeai as genai

from common.logger import get_logger
from search.config import SearchConfig

config = SearchConfig()
logger = get_logger(
    __name__, config.LOG_LEVEL, config.LOG_TO_CONSOLE, config.LOG_TO_FILE
)

genai.configure(api_key=config.GEMINI_API_KEY)
model = genai.GenerativeModel(config.LLM_MODEL)


def build_parsing_prompt(query):
    """
    Build the prompt for LLM query parsing

    Args:
        query: User query

    Returns:
        Formatted prompt
    """
    prompt = f"""You are a query parser for a job search system. Parse the user's natural language query into structured filters and semantic search intent.

    User Query: "{query}"

    Available Job Levels:
    - Senior Level
    - Mid Level
    - Entry Level
    - Internship

    Available Job Categories (examples):
    - Software Engineering
    - Data and Analytics
    - Design and UX
    - Sales
    - Project Management
    - Advertising and Marketing
    - General

    Instructions:
    1. Extract the SEMANTIC SEARCH INTENT (what skills, roles, technologies the user wants)
    2. Extract FILTERS (job level, category, company, location if mentioned)
    3. Only include filters that are explicitly mentioned or strongly implied
    4. Keep semantic query focused on skills, roles, and technologies
    5. Keep strong focus that the semantic_query should not be empty there should be something relevant to the query
    6. There may be the industry related query like it,sales,marketing so if that occurs then make sure that it industry you make category for Software Engineering, Data and Analytics, Design and UX, similar for others
    7. For broad location terms, use keywords that will match partial locations:
       - "Bay Area" → use "San Francisco" or "California" 
       - "Asia" → use "Asia" or "India" or "China" (will match cities with country names)
       - "Europe" → use "Europe" or specific countries
       - Keep the broad term as-is for text matching to work
    8. For date/time queries, extract the number of days:
       - "recent" or "latest" → 7 days
       - "last week" → 7 days
       - "last month" or "last 30 days" → 30 days
       - "last 2 weeks" → 14 days
       - "this year" or "last year" → 365 days
       - "last 6 months" → 180 days
       - "last 3 months" → 90 days
       - For specific years mentioned (e.g., "2024", "2025") → calculate days from start of that year to now
       - If no specific timeframe mentioned, don't add date_range

    Return ONLY a JSON object in this exact format:
    {{
        "semantic_query": "core search terms focusing on skills and role",
        "filters": {{
            "category": "category name if mentioned or null",
            "Level": "job level if mentioned or null",
            "company": "company name if mentioned or null",
            "location": "location if mentioned or null",
            "date_range": {{
                "days": number of days for recent jobs (e.g., 30 for last 30 days) or null
            }}
        }}
    }}

    Examples:

    Query: "Senior Python developer jobs in San Francisco"
    {{
        "semantic_query": "Python developer",
        "filters": {{
            "Level": "Senior Level",
            "location": "San Francisco"
        }}
    }}

    Query: "Looking for data scientist positions at Google"
    {{
        "semantic_query": "data scientist",
        "filters": {{
            "category": "Data and Analytics",
            "company": "Google"
        }}
    }}

    Query: "Entry level frontend developer with React experience"
    {{
        "semantic_query": "frontend developer React",
        "filters": {{
            "Level": "Entry Level",
            "category": "Software Engineering"
        }}
    }}

    Query: "jobs in New York",
    {{
        "semantic_query": "jobs",
        "filters": {{
            "location": "New York"
        }}
    }}

    Query: "software engineer in Bay Area"
    {{
        "semantic_query": "software engineer",
        "filters": {{
            "category": "Software Engineering",
            "location": "San Francisco"
        }}
    }}

    Query: "data analyst jobs in Asia"
    {{
        "semantic_query": "data analyst",
        "filters": {{
            "category": "Data and Analytics",
            "location": "India"
        }}
    }}

    Query: "senior developer positions in Europe"
    {{
        "semantic_query": "developer",
        "filters": {{
            "Level": "Senior Level",
            "location": "Europe"
        }}
    }}

    Query: "data scientist jobs posted in last 30 days"
    {{
        "semantic_query": "data scientist",
        "filters": {{
            "category": "Data and Analytics",
            "date_range": {{
                "days": 30
            }}
        }}
    }}

    Query: "recent python developer positions"
    {{
        "semantic_query": "python developer",
        "filters": {{
            "category": "Software Engineering",
            "date_range": {{
                "days": 7
            }}
        }}
    }}

    Query: "jobs from last week"
    {{
        "semantic_query": "jobs",
        "filters": {{
            "date_range": {{
                "days": 7
            }}
        }}
    }}

    Query: "python jobs posted this year"
    {{
        "semantic_query": "python",
        "filters": {{
            "category": "Software Engineering",
            "date_range": {{
                "days": 365
            }}
        }}
    }}

    Query: "senior engineer positions from last 6 months"
    {{
        "semantic_query": "senior engineer",
        "filters": {{
            "Level": "Senior Level",
            "date_range": {{
                "days": 180
            }}
        }}
    }}

    Now parse the user's query. Return ONLY the JSON object, no other text."""

    return prompt


def extract_json_from_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON object from LLM response

    Args:
        response_text: LLM response text

    Returns:
        Parsed JSON dict or None
    """

    try:
        # Try to find JSON object in response
        # Look for content between first { and last }
        start = response_text.find("{")
        end = response_text.rfind("}") + 1

        if start != -1 and end > start:
            json_str = response_text[start:end]
            result = json.loads(json_str)

            # Clean up filters (remove null values)
            if "filters" in result:
                # Handle date_range conversion
                if (
                    "date_range" in result["filters"]
                    and result["filters"]["date_range"]
                ):
                    date_range_input = result["filters"]["date_range"]
                    if (
                        isinstance(date_range_input, dict)
                        and "days" in date_range_input
                    ):
                        days = date_range_input["days"]
                        if days:
                            # Calculate date range
                            now = datetime.now(timezone.utc)
                            past_date = now - timedelta(days=days)

                            # Convert to RFC 3339 format with 'Z' suffix to match data format
                            result["filters"]["date_range"] = {
                                "gte": past_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "lte": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "gt": None,
                                "lt": None,
                            }
                            logger.debug(
                                f"converted date_range to proper format from last {days} days"
                            )
                        else:
                            result["filters"]["date_range"] = None

                # Remove null values
                result["filters"] = {
                    k: v
                    for k, v in result["filters"].items()
                    if v is not None and v != "" and v != "null"
                }

            return result
        else:
            logger.warning("No JSON object found in LLM response")
            return None

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error :{e}")
        logger.debug(f"Response text:{response_text}")
        return None


def convert_query_to_semantic_and_filter(query):
    """Convert natural language query to semantic query and filters

    Args:
        query: Natural language search query

    Returns:
        Dictionary with semantic_query and filters
    """
    logger.info(f"Parsing query:{query}")
    prompt = build_parsing_prompt(query)
    logger.debug("Sending query to LLM for parsing")

    start_time = datetime.now()

    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=config.LLM_TEMPERATURE,
            max_output_tokens=config.LLM_MAX_TOKENS,
        ),
    )
    elapsed = (datetime.now() - start_time).total_seconds()
    logger.debug(f"LLM response received in {elapsed:.2f}s")
    result = extract_json_from_response(response.text)

    if result:
        logger.info("Query parsed successfully")
    else:
        logger.warning("Failed to parse LLM response")

    return result
