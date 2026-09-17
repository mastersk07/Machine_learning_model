"""Web search - no API key required (duckduckgo-search)."""


def search(query: str, max_results: int = 5) -> str:
    try:
        from ddgs import DDGS
    except ImportError:
        return "Web search isn't available: run `pip install -r requirements.txt` first."

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
    except Exception as exc:  # noqa: BLE001
        return f"Web search failed: {exc}"

    if not results:
        return f"No results found for '{query}'."

    lines = [f"Top results for '{query}':"]
    for i, r in enumerate(results, 1):
        title = r.get("title", "").strip()
        href = r.get("href", "").strip()
        body = r.get("body", "").strip()
        lines.append(f"{i}. {title}\n   {href}\n   {body}")
    return "\n".join(lines)
