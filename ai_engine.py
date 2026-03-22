import json
from google import genai
from google.genai import types
from pydantic import BaseModel


# --- DEFINE STRICT OUTPUT SCHEMA ---
# This guarantees Gemini will return exactly this structure without hallucinating formatting.
class GraphData(BaseModel):
    skills: list[str]
    experience: list[str]
    education: list[str]


class ResumeAnalysis(BaseModel):
    candidate_name: str
    ats_score: int
    matching_skills: list[str]
    missing_skills: list[str]
    suggestions: list[str]
    graph_data: GraphData


def analyze_resume(resume_text, target_role, api_key):
    """Sends the resume text to Gemini 3 Flash using the latest SDK and Pydantic schemas."""

    prompt = f"""
    You are an expert ATS (Applicant Tracking System) and Career Coach. 
    Analyze the following resume against the target role: "{target_role}".
    Be critical but constructive.

    Resume Text:
    {resume_text}
    """

    try:
        # 1. Initialize the new SDK Client using the user's API Key
        client = genai.Client(api_key=api_key)

        # 2. Call the Gemini 3 Flash Preview model
        response = client.models.generate_content(
            model='gemini-3.0-flash-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ResumeAnalysis,  # Force strict JSON schema
                temperature=0.2,  # Lower temperature for analytical precision
            )
        )

        # Return the strictly formatted JSON response as a dictionary
        return json.loads(response.text)

    except Exception as e:
        return {"error": str(e)}