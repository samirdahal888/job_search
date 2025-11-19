#  LLM response in clear and natural language

import google.generativeai as genai

from config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


def LLM_response(unique_job_results, original_query):
    formatted_unique_jobs = format_job_for_response(unique_job_results)
    prompt = prompt_for_llm_response(formatted_unique_jobs, original_query)

    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=settings.LLM_TEMPERATURE,
            max_output_tokens=settings.LLM_MAX_TOKENS,
        ),
    )

    return response.text.strip()


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

    return prompt
