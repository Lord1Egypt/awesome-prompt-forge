#!/usr/bin/env python3
"""Build index.json from all prompts in the prompts/ directory."""

import os
import json
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPTS_DIR = os.path.join(PROJECT_ROOT, "prompts")
OUT_PATH = os.path.join(PROJECT_ROOT, "index.json")

CATEGORIES = [
    "claude", "chatgpt", "v0", "cursor", "copilot",
    "grok", "devin", "perplexity", "llama",
    "writing", "general", "tools"
]

prompts = []

for category in CATEGORIES:
    cat_dir = os.path.join(PROMPTS_DIR, category)
    if not os.path.isdir(cat_dir):
        continue
    for fname in sorted(os.listdir(cat_dir)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(cat_dir, fname)
        with open(fpath, encoding="utf-8") as f:
            content = f.read()
        # extract first heading as description
        desc = ""
        m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if m:
            desc = m.group(1).strip()
        else:
            # use first non-empty line
            for line in content.splitlines():
                line = line.strip()
                if line:
                    desc = line[:100]
                    break
        name = fname[:-3]  # strip .md
        prompts.append({
            "name": name,
            "category": category,
            "description": desc,
            "path": f"prompts/{category}/{fname}"
        })

index = {"version": "1.0.0", "total": len(prompts), "prompts": prompts}

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(index, f, indent=2, ensure_ascii=False)

print(f"index.json written — {len(prompts)} prompts")
for cat in CATEGORIES:
    count = sum(1 for p in prompts if p["category"] == cat)
    if count:
        print(f"  {cat:<15} {count}")
