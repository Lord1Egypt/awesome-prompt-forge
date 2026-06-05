import json
import os
from typing import Optional

_PROMPTS_ROOT = os.path.join(os.path.dirname(__file__), "prompts")
_INDEX_PATH = os.path.join(os.path.dirname(__file__), "index.json")

_index: Optional[dict] = None


def _get_index() -> dict:
    global _index
    if _index is None:
        with open(_INDEX_PATH, encoding="utf-8") as f:
            _index = json.load(f)
    return _index


class Prompt:
    def __init__(self, meta: dict, content: str):
        self.name = meta["name"]
        self.category = meta["category"]
        self.description = meta["description"]
        self.path = meta["path"]
        self.content = content

    def __repr__(self):
        return f"<Prompt name={self.name!r} category={self.category!r}>"

    def __str__(self):
        return self.content


def load(name: str, category: str = None) -> Prompt:
    """
    Load a prompt by name. Reads from disk only when called.

    Args:
        name: Prompt name (e.g. "claude-5-06-2025")
        category: Optional — "claude", "chatgpt", "v0", "cursor", etc.

    Returns:
        Prompt object with .content, .name, .category, .description

    Example:
        p = load("claude-5-06-2025")
        print(p.content)
    """
    index = _get_index()
    matches = [
        p for p in index["prompts"]
        if p["name"] == name and (category is None or p["category"] == category)
    ]
    if not matches:
        raise ValueError(
            f"Prompt '{name}' not found. Use search('{name}') to find similar prompts."
        )
    if len(matches) > 1 and category is None:
        cats = [m["category"] for m in matches]
        raise ValueError(
            f"Prompt '{name}' exists in multiple categories: {cats}. "
            f"Specify category=, e.g. load('{name}', category='{cats[0]}')"
        )
    meta = matches[0]
    rel = meta["path"].split("prompts/", 1)[1]
    prompt_path = os.path.join(_PROMPTS_ROOT, *rel.split("/"))
    with open(prompt_path, encoding="utf-8") as f:
        content = f.read()
    return Prompt(meta, content)


def search(query: str, category: str = None, limit: int = 10) -> list:
    """
    Search prompts by name or description keyword.

    Args:
        query: Search term
        category: Optional filter
        limit: Max results (default 10)

    Returns:
        List of dicts with name, category, description

    Example:
        results = search("linux terminal")
        for r in results:
            print(r["name"], r["category"])
    """
    index = _get_index()
    q = query.lower()
    results = [
        p for p in index["prompts"]
        if (q in p["name"].lower() or q in p["description"].lower())
        and (category is None or p["category"] == category)
    ]
    return [{"name": r["name"], "category": r["category"], "description": r["description"]}
            for r in results[:limit]]


def list_prompts(category: str = None) -> list:
    """
    List all prompts, optionally filtered by category.

    Args:
        category: Optional — "claude", "chatgpt", "v0", "cursor", etc.

    Returns:
        List of dicts with name, category, description

    Example:
        prompts = list_prompts(category="claude")
        print(len(prompts))
    """
    index = _get_index()
    prompts = index["prompts"]
    if category:
        prompts = [p for p in prompts if p["category"] == category]
    return [{"name": p["name"], "category": p["category"], "description": p["description"]}
            for p in prompts]


def categories() -> dict:
    """
    Return prompt counts per category.

    Returns:
        Dict with category names and counts

    Example:
        print(categories())
        # {"claude": 12, "chatgpt": 180, ..., "total": 350}
    """
    index = _get_index()
    counts = {}
    for p in index["prompts"]:
        counts[p["category"]] = counts.get(p["category"], 0) + 1
    counts["total"] = index["total"]
    return counts
