"""
awesome-prompt-forge — Lazy-loading AI system prompts toolkit
350+ real-world prompts from Claude, ChatGPT, v0, Cursor, Grok, Devin & more.
"""

from .loader import load, search, list_prompts, categories

__version__ = "1.0.0"
__all__ = ["load", "search", "list_prompts", "categories"]
