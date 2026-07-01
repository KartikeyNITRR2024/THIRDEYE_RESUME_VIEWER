import os
import json
import logging
from pathlib import Path
from google import genai

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("gemini_client")

PROMPT_PATH = Path(__file__).parent / "prompt.md"

def _load_prompt(resume_text: str, job_description: str, company_name: str, years_exp: str) -> str:
    logger.debug("Loading prompt template from disk.")
    template = PROMPT_PATH.read_text(encoding="utf-8")
    prompt = (
        template
        .replace("{{RESUME_TEXT}}", resume_text)
        .replace("{{JOB_DESCRIPTION}}", job_description)
        .replace("{{COMPANY_NAME}}", company_name)
        .replace("{{YEARS_EXP}}", years_exp)
    )
    logger.debug("Prompt template populated successfully.")
    return prompt

def generate_resume_json(
    gemini_key: str, 
    gemini_model: str, 
    resume_text: str, 
    job_description: str, 
    company_name: str, 
    years_exp: str
) -> dict:
    
    model_to_use = gemini_model if gemini_model else os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    logger.info(f"Initializing Gemini client with model: {model_to_use}")

    client = genai.Client(api_key=gemini_key)
    prompt = _load_prompt(resume_text, job_description, company_name, years_exp)

    logger.debug("Sending request to Gemini API.")
    try:
        response = client.models.generate_content(
            model=model_to_use,
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
    except Exception as e:
        logger.error(f"Gemini API request failed: {str(e)}")
        raise e

    raw = response.text.strip()
    logger.debug("Received raw response from Gemini.")

    if raw.startswith("```"):
        logger.debug("Stripping markdown code fences from response.")
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()

    try:
        data = json.loads(raw)
        logger.info("Successfully parsed Gemini response to JSON.")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode Gemini response: {str(e)}")
        raise ValueError(f"Gemini did not return valid JSON: {e}\nRaw output: {raw[:500]}")


@app.get("/health")
async def health_check():
    return {"status": "ok"}