import config


def is_ai_available():
    """Returns True only if an API key has been configured."""
    return bool(config.AI_API_KEY.strip())


def ask_ai_for_help(error_type, code_snippet, raw_message):
    """
    Sends the error details to Claude for a more detailed explanation.
    Returns a plain string response, or a friendly offline message on
    any failure (no key configured, no internet, API error).
    """
    if not is_ai_available():
        return ("Online AI Assistance is not set up on this computer. "
                "The offline explanation above is still fully accurate - "
                "AI assistance is just an optional extra.")

    try:
        import requests
    except ImportError:
        return "Online AI Assistance requires the 'requests' library, which is not installed."

    prompt = (
        f"A Class 12 student got this Python error: {error_type}\n"
        f"Message: {raw_message}\n"
        f"Their code:\n{code_snippet}\n\n"
        "Explain in 3-4 simple sentences, beginner-friendly, why this happened "
        "and how to fix it. Do not just repeat the error message."
    )

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": config.AI_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": config.AI_MODEL,
                "max_tokens": 400,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=8
        )
        response.raise_for_status()
        data = response.json()
        text_parts = [block["text"] for block in data.get("content", []) if block.get("type") == "text"]
        return "\n".join(text_parts) if text_parts else "The AI did not return a usable response."

    except Exception:
        # Covers: no internet, timeout, invalid key, API downtime, etc.
        return ("Online AI Assistance is currently unavailable (no internet connection "
                "or the service could not be reached). Offline Mode is still active - "
                "the explanation above remains fully usable.")
