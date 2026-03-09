from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()
GOOGLE_API = os.getenv("google_api")
client = genai.Client(api_key=GOOGLE_API)


def get_audit_result(file_bytes):
    prompt = """You are a UK Property Law expert. Analyze this tenancy agreement based on the Renters' Rights Act 2026.
    
    Check for:
    1. 'Section 21' or 'No-fault' clauses (now illegal).
    2. Fixed-term clauses (must be periodic/rolling).
    3. Rent increase clauses (limited to once per year).
    
    Provide a 'Compliance Score' (0-100) and list specific legal issues found. Conclude by reminding the user to verify these findings with a legal professional.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=[
            types.Part.from_bytes(
                data=file_bytes,
                mime_type="application/pdf",
            ),
            prompt,
        ],
    )
    return response.text
