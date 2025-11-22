"""LLM response generation for search results"""

from datetime import datetime

import google.generativeai as genai

from api_config import api_config
from common.logger import get_logger
from search.config import SearchConfig

config = SearchConfig()
logger = get_logger(
    __name__, config.LOG_LEVEL, config.LOG_TO_CONSOLE, config.LOG_TO_FILE
)

genai.configure(api_key=config.GEMINI_API_KEY)
model = genai.GenerativeModel(config.LLM_MODEL)


def get_llm_response(unique_job_results, original_query):
    """Generate natural language response from search results

    Args:
        unique_job_results: List of unique job results
        original_query: Original user query

    Returns:
        Generated response text
    """
    logger.info(f"Generating LLM response for {len(unique_job_results)} jobs")
    formatted_unique_jobs = format_job_for_response(unique_job_results)
    prompt = prompt_for_llm_response(formatted_unique_jobs, original_query)

    logger.debug("Sending request to LLM for response generation")

    start_time = datetime.now()
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=config.LLM_TEMPERATURE,
            max_output_tokens=config.LLM_MAX_TOKENS,
        ),
    )
    elapsed = (datetime.now() - start_time).total_seconds()
    response_text = response.text.strip()

    logger.info(
        f"LLM response generated in {elapsed:.2f}s , {len(response_text)} chars"
    )
    logger.debug(f"Response preview: {response_text[:100]}...")

    return response_text


def format_job_for_response(unique_job_results):
    """Format job results for LLM prompt

    Args:
        unique_job_results: List of job results

    Returns:
        Formatted string representation of jobs
    """
    data = []
    for i, point in enumerate(unique_job_results, 1):
        data.append(f"Rank:{i}")
        data.append(f"Score: {point.score:.4f}")
        data.append(
            f"Job Title: {point.payload.get('job_title', api_config.DEFAULT_MISSING_VALUE)}"
        )
        data.append(
            f"Company: {point.payload.get('company', api_config.DEFAULT_MISSING_VALUE)}"
        )
        data.append(
            f"Location: {point.payload.get('location', api_config.DEFAULT_MISSING_VALUE)}"
        )
        data.append(
            f"Job Level: {point.payload.get('Level', api_config.DEFAULT_MISSING_VALUE)}"
        )
        data.append(
            f"Category: {point.payload.get('category', api_config.DEFAULT_MISSING_VALUE)}"
        )
        data.append(
            f"Publication Date: {point.payload.get('publication_date', api_config.DEFAULT_MISSING_VALUE)}"
        )

        data.append(f"Job ID: {point.payload.get('chunk_id', 'N/A')}")
        data.append(f"Description:\n {point.payload.get('text', 'N/A')}")
        data.append("-" * 80)
    return "\n".join(data)


def prompt_for_llm_response(formatted_jobs, query):
    """Create prompt for LLM response generation

    Args:
        formatted_jobs: Formatted job results string
        query: Original user query

    Returns:
        Formatted prompt
    """
    prompt = f"""You are an intelligent job search assistant. Based on the user's query and the search results, 
provide a helpful, natural language response.

User Query: "{query}"

Search Results:
{formatted_jobs}

Instructions:
1. Provide a clear, conversational summary of the search results
2. Highlight key matches and relevant job details
3. Mention job titles, companies, locations, and levels when relevant
4. If there are multiple jobs, briefly summarize the variety available
5. Be concise but informative (2-4 sentences)
6. Don't use technical jargon like "score" or "rank"
7. Focus on what would be most helpful to the job seeker

Generate your response:"""

    return prompt
