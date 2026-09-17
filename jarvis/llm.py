"""TensorX chat client.

IMPORTANT: this environment's network egress proxy blocks api.tensorx.ai
entirely, so this client has never been exercised against the real API.
It assumes an OpenAI-compatible `/chat/completions` endpoint (base_url +
"/chat/completions", Authorization: Bearer <key>, {"model", "messages"} in,
choices[0].message.content out) because that's the most common contract for
hosted LLM APIs. Run `python -m jarvis.llm` on a machine that can actually
reach TensorX to confirm this - if it fails, paste the real error/response
body back and the request/response handling below can be adjusted to match.
"""
import requests

from jarvis import config


class TensorXError(RuntimeError):
    pass


def chat(messages: list[dict], temperature: float = 0.7) -> str:
    """Send a chat completion request to TensorX. `messages` is a list of
    {"role": "system"|"user"|"assistant", "content": str} dicts."""
    if not config.TENSORX_API_KEY:
        raise TensorXError(
            "TENSORX_API_KEY is not set. Add it to your .env file."
        )

    url = f"{config.TENSORX_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.TENSORX_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config.TENSORX_MODEL,
        "messages": messages,
        "temperature": temperature,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
    except requests.RequestException as exc:
        raise TensorXError(f"Could not reach TensorX at {url}: {exc}") from exc

    if resp.status_code != 200:
        raise TensorXError(
            f"TensorX returned HTTP {resp.status_code}: {resp.text[:500]}"
        )

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise TensorXError(
            "TensorX response didn't match the expected OpenAI-style shape. "
            f"Raw response: {data}"
        ) from exc


def list_models() -> list:
    """Hits /models - useful as a quick connectivity/auth smoke test."""
    if not config.TENSORX_API_KEY:
        raise TensorXError("TENSORX_API_KEY is not set. Add it to your .env file.")

    url = f"{config.TENSORX_BASE_URL.rstrip('/')}/models"
    headers = {"Authorization": f"Bearer {config.TENSORX_API_KEY}"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    print("Checking TensorX connectivity...")
    try:
        print(list_models())
    except Exception as exc:  # noqa: BLE001
        print(f"Failed: {exc}")
