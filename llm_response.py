#  LLM response in clear and natural language

import google.generativeai as genai
from datetime import datetime

from config import settings
from logger import get_logger
logger = get_logger(__name__)

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.LLM_MODEL)


def LLM_response(unique_job_results, original_query):
    logger.info(f"Generating LLM response for {len(unique_job_results)} jobs")
    formatted_unique_jobs = format_job_for_response(unique_job_results)
    prompt = prompt_for_llm_response(formatted_unique_jobs, original_query)

    logger.debug("Sending request to LLM for response generation")

    start_time = datetime.now()
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=settings.LLM_TEMPERATURE,
            max_output_tokens=settings.LLM_MAX_TOKENS,
        ),
    )
    elapsed = (datetime.now()-start_time).total_seconds()
    response_text = response.text.strip()

    logger.info(f"LLM response generated in {elapsed:.2f}s , {len(response_text)} chars")
    logger.debug(f"Response preview: {response_text[:100]}...")

    return response_text


def format_job_for_response(unique_job_results):
    # this function  helps to make the data in string in nice and beautiful line format
    # after this we can send this formated data in the LLM
    data = []
    for i, point in enumerate(unique_job_results, 1):
        data.append(f"Rank:{i}")
        data.append(f"Score: {point.score:.4f}")
        data.append(f"Job Title: {point.payload.get('job_title', 'N/A')}")
        data.append(f"Company: {point.payload.get('company', 'N/A')}")
        data.append(f"Category: {point.payload.get('category', 'N/A')}")
        data.append(f"Location: {point.payload.get('location', 'N/A')}")
        data.append(f"Level: {point.payload.get('Level', 'N/A')}")
        data.append(f"Chunk ID: {point.payload.get('chunk_id', 'N/A')}")

        # Display text snippet (first 300 characters)
        text = point.payload.get("text", "")
        snippet = text[:300] + "..." if len(text) > 300 else text
        data.append(f"Description:{snippet}")

    logger.info("Formatting jobs to input in the LLM")

    return "\n".join(data)


def prompt_for_llm_response(jobs_text, original_query):
    prompt = f"""You are a job search assistant. Provide a summary of search results.

    USER QUERY: "{original_query}"

    JOBS:
    {jobs_text}

    Generate a concise summary (3-4 sentences) that:
    1. States how many relevant jobs were found
    2. Highlights the most relevant match
    3. Mentions variety/commonalities (companies, locations, levels)
    4. Suggests reviewing the details

    Keep it brief and actionable.

    Summary:"""
    logger.info("Created proper prompt with user query and jobs text for LLM response")
    return prompt
