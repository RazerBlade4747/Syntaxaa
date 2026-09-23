"""
modules/ai_debugger.py
----------------------
Handles AI-powered error explanations using Google GenAI SDK (Gemini API)
with full offline detection and fallback handling.
"""

from google import genai
from google.genai import types
import config
import database


def is_network_available():
    """Checks if the app is explicitly set to offline."""
    if database.FORCE_OFFLINE:
        return False
    if not hasattr(config, "GEMINI_API_KEY") or not config.GEMINI_API_KEY:
        return False
    return True


def explain_error_with_gemini(code_snippet: str, error_message: str) -> str:
    """Generates AI analysis."""
    if not is_network_available():
        return (
            "⚠️ NETWORK NOT AVAILABLE (OFFLINE MODE)\n\n"
            "AI Debugger requires an active internet connection and a valid GEMINI_API_KEY in config.py.\n\n"
            "Local Rule-Based Analysis is active. Switch to 'Problems' "
            "tabs to view offline error analysis."
        )

    try:
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        prompt = f"""
You are an expert Python debugging assistant for SYNTAXAA.
Analyze the following code and traceback.

Provide:
1. **What went wrong** (1-2 sentences)
2. **Why it happened**
3. **How to fix it** (with corrected snippet)

--- CODE ---
{code_snippet}

--- TRACEBACK ---
{error_message}
"""
        # Set to gemini-3.6-flash as instructed by the API endpoint
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3)
        )
        return response.text if response.text else "No explanation generated."
    except Exception as e:
        return (
            f"⚠️ NETWORK / API CONNECTION ERROR\n\n"
            f"Failed to connect to Gemini API: {str(e)}\n\n"
            "Operating in local offline mode."
        )