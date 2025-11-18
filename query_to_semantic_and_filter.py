import json
import os
from typing import Any, Dict, Optional

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


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
    5 . Keep strong focus that  the sementic_query should not be empty there should be something relevent to the query
    6. There may be the industry related query like it,sales,marketing so if that occure then make sure that it instry you make category for  Software Engineering
    - Data and Analytics
    - Design and UX , similar for others

    Return ONLY a JSON object in this exact format:
    {{
        "semantic_query": "core search terms focusing on skills and role",
        "filters": {{
            "category": "category name if mentioned or null",
            "Level": "job level if mentioned or null",
            "company": "company name if mentioned or null",
            "location": "location if mentioned or null"
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
        "semantic_query": "New York jobs",
        "filters": {{
            "Location": "New York"
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
                result["filters"] = {
                    k: v
                    for k, v in result["filters"].items()
                    if v is not None and v != "" and v != "null"
                }

            return result
        else:
            print("⚠️  No JSON found in LLM response")
            return None

    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parsing error: {e}")
        print(f"Response: {response_text[:200]}")
        return None


def convert_query_to_semantic_and_filter(query):
    prompt = build_parsing_prompt(query)

    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.3,
            max_output_tokens=10000,
        ),
    )
    print(f"this is the llm response ============= {response}")

    result = extract_json_from_response(response.text)
    finish_reason = response.candidates[0].finish_reason
    print(finish_reason)

    return result
