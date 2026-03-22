import json
from google import genai
from google.genai import types
from pydantic import BaseModel


# --- ENHANCED GRAPH SCHEMA ---
class ExperienceDetail(BaseModel):
    title: str
    organization: str


class EducationDetail(BaseModel):
    degree: str
    institution: str


class GraphData(BaseModel):
    matched_skills: list[str]
    missing_skills: list[str]
    experience: list[ExperienceDetail]
    education: list[EducationDetail]


class ResumeAnalysis(BaseModel):
    candidate_name: str
    ats_score: int
    matching_skills: list[str]
    missing_skills: list[str]
    suggestions: list[str]
    graph_data: GraphData


def analyze_resume(resume_text, target_role, api_key):
    prompt = f"""
    You are an expert ATS and Career Coach. 
    Analyze the following resume against the target role: "{target_role}".
    Extract precise graph data including organizations and degrees.
    Resume Text:
    {resume_text}
    """
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ResumeAnalysis,
                temperature=0.2,
            )
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e)}


def chat_with_resume(prompt, resume_text, chat_history, api_key):
    try:
        client = genai.Client(api_key=api_key)
        system_instruction = f"You are an elite Career Coach. Base answers ONLY on this resume context:\n{resume_text}"

        contents = [{"role": "user", "parts": [{"text": system_instruction}]}]
        for msg in chat_history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        contents.append({"role": "user", "parts": [{"text": prompt}]})

        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=contents,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        return response.text
    except Exception as e:
        return f"Error connecting to Chat AI: {str(e)}"