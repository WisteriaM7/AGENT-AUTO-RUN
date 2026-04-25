import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3"  # Change to your installed model, e.g. mistral, phi3, gemma


def call_ollama(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """
    Sends a prompt to the local Ollama instance and returns the response text.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except requests.exceptions.ConnectionError:
        return (
            "⚠️ Could not connect to Ollama. "
            "Make sure Ollama is running (`ollama serve`) and the model is pulled."
        )
    except requests.exceptions.Timeout:
        return "⚠️ Ollama request timed out. The model may be too slow or the prompt too long."
    except Exception as e:
        return f"⚠️ Ollama error: {str(e)}"
