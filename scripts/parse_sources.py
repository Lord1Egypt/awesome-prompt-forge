#!/usr/bin/env python3
"""
Parse all prompt data sources and organize into prompts/ by category.
Output: /home/lordegypt/awesome-prompt-forge/prompts/<category>/<name>.md
"""

import os
import re
import csv
import shutil

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPTS_DIR = os.path.join(PROJECT_ROOT, "prompts")

HF_ROOT = "/home/lordegypt/hf-prompt-datasets"
AWESOME_AI_ROOT = "/home/lordegypt/awesome-ai-system-prompts"

NYMBO_DIR = os.path.join(HF_ROOT, "Nymbo--Official_LLM_System_Prompts")
MORITZ_DIR = os.path.join(HF_ROOT, "MoritzLaurer--closed_system_prompts")
FKA_CSV = os.path.join(HF_ROOT, "fka--awesome-chatgpt-prompts", "prompts.csv")
DANIEL_DIR = os.path.join(HF_ROOT, "danielrosehill--Writing-System-Prompts")


def slugify(name):
    name = re.sub(r'[^\w\s-]', '', name.lower())
    name = re.sub(r'[\s_]+', '-', name.strip())
    name = re.sub(r'-+', '-', name)
    return name[:80]


def write_prompt(category, name, content, source=""):
    cat_dir = os.path.join(PROMPTS_DIR, category)
    os.makedirs(cat_dir, exist_ok=True)
    safe_name = slugify(name) + ".md"
    out_path = os.path.join(cat_dir, safe_name)
    # avoid duplicates — append suffix
    if os.path.exists(out_path):
        base = slugify(name)
        i = 2
        while os.path.exists(os.path.join(cat_dir, f"{base}-{i}.md")):
            i += 1
        safe_name = f"{base}-{i}.md"
        out_path = os.path.join(cat_dir, safe_name)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    return safe_name


def classify_nymbo(filename):
    f = filename.lower()
    if f.startswith("claude"):
        return "claude"
    if any(f.startswith(p) for p in ["chatgpt", "gpt-", "o3", "o4", "gpt builder"]):
        return "chatgpt"
    if f.startswith("vercel v0") or f.startswith("v0"):
        return "v0"
    if "copilot" in f:
        return "copilot"
    if f.startswith("grok"):
        return "grok"
    if f.startswith("devin"):
        return "devin"
    if f.startswith("perplexity"):
        return "perplexity"
    if f.startswith("llama"):
        return "llama"
    if f.startswith("cursor"):
        return "cursor"
    if f.startswith("mistral"):
        return "tools"
    return "tools"


def parse_nymbo():
    print("\n[1/5] Parsing Nymbo Official LLM System Prompts...")
    count = 0
    for fname in os.listdir(NYMBO_DIR):
        if not fname.endswith(".md"):
            # some entries are folders (ChatGPT Search iOS)
            full = os.path.join(NYMBO_DIR, fname)
            if os.path.isdir(full):
                for sub in os.listdir(full):
                    if sub.endswith(".md"):
                        with open(os.path.join(full, sub), encoding="utf-8") as f:
                            content = f.read()
                        category = classify_nymbo(fname)
                        name = os.path.splitext(fname)[0] + " - " + os.path.splitext(sub)[0]
                        write_prompt(category, name, content, "nymbo")
                        count += 1
            continue
        with open(os.path.join(NYMBO_DIR, fname), encoding="utf-8") as f:
            content = f.read()
        name = os.path.splitext(fname)[0]
        category = classify_nymbo(fname)
        write_prompt(category, name, content, "nymbo")
        count += 1
    print(f"  → {count} prompts")


def parse_moritz():
    print("\n[2/5] Parsing MoritzLaurer closed system prompts...")
    count = 0
    for fname in os.listdir(MORITZ_DIR):
        if not fname.endswith(".yaml"):
            continue
        with open(os.path.join(MORITZ_DIR, fname), encoding="utf-8") as f:
            raw = f.read()
        # Extract content from YAML — pull out the 'content' field value
        content_match = re.search(r'content:\s*\|-?\n(.*?)(?=\n\s*-\s*role:|\Z)', raw, re.DOTALL)
        if content_match:
            content = content_match.group(1)
            # de-indent by 8 spaces (YAML block indent)
            lines = content.split('\n')
            dedented = []
            for line in lines:
                if line.startswith('        '):
                    dedented.append(line[8:])
                elif line.startswith('      '):
                    dedented.append(line[6:])
                else:
                    dedented.append(line)
            content = '\n'.join(dedented).strip()
        else:
            content = raw  # fallback: include raw YAML

        name = os.path.splitext(fname)[0]
        if "claude" in fname:
            category = "claude"
        else:
            category = "chatgpt"
        write_prompt(category, name, content, "moritz")
        count += 1
    print(f"  → {count} prompts")


def parse_fka():
    print("\n[3/5] Parsing fka/awesome-chatgpt-prompts CSV...")
    count = 0
    csv.field_size_limit(10 * 1024 * 1024)
    with open(FKA_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            act = row.get("act", "").strip()
            prompt = row.get("prompt", "").strip()
            if not act or not prompt:
                continue
            name = f"act-as-{act}"
            content = f"# Act as {act}\n\n{prompt}\n"
            write_prompt("general", name, content, "fka")
            count += 1
    print(f"  → {count} prompts")


def parse_danielrosehill():
    print("\n[4/5] Parsing danielrosehill Writing System Prompts...")
    count = 0
    for entry in os.listdir(DANIEL_DIR):
        if entry == "README.md":
            continue
        entry_path = os.path.join(DANIEL_DIR, entry)
        if os.path.isdir(entry_path):
            for fname in os.listdir(entry_path):
                if fname.endswith(".md"):
                    with open(os.path.join(entry_path, fname), encoding="utf-8") as f:
                        content = f.read()
                    name = os.path.splitext(fname)[0]
                    write_prompt("writing", name, content, "danielrosehill")
                    count += 1
        elif entry.endswith(".md"):
            with open(entry_path, encoding="utf-8") as f:
                content = f.read()
            name = os.path.splitext(entry)[0]
            write_prompt("writing", name, content, "danielrosehill")
            count += 1
    print(f"  → {count} prompts")


def classify_awesome_ai(folder):
    f = folder.lower()
    if "claude" in f:
        return "claude"
    if "chatgpt" in f:
        return "chatgpt"
    if f == "v0":
        return "v0"
    if "grok" in f:
        return "grok"
    if "cursor" in f:
        return "cursor"
    if "devin" in f:
        return "devin"
    if "perplexity" in f:
        return "perplexity"
    if "copilot" in f:
        return "copilot"
    if "mistral" in f:
        return "tools"
    if "google" in f:
        return "tools"
    return "tools"


def parse_awesome_ai():
    print("\n[5/5] Parsing Lord1Egypt/awesome-ai-system-prompts...")
    count = 0
    skip = {"LICENSE", "README.md", "readme_old.md", ".git"}
    for entry in os.listdir(AWESOME_AI_ROOT):
        if entry in skip or entry.startswith("."):
            continue
        entry_path = os.path.join(AWESOME_AI_ROOT, entry)
        category = classify_awesome_ai(entry)
        if os.path.isdir(entry_path):
            for fname in os.listdir(entry_path):
                if fname.endswith(".md") and fname.lower() != "readme.md":
                    with open(os.path.join(entry_path, fname), encoding="utf-8") as f:
                        content = f.read()
                    name = f"{entry}-{os.path.splitext(fname)[0]}"
                    write_prompt(category, name, content, "awesome-ai")
                    count += 1
        elif entry.endswith(".md") and entry.lower() != "readme.md":
            with open(entry_path, encoding="utf-8") as f:
                content = f.read()
            name = os.path.splitext(entry)[0]
            write_prompt(category, name, content, "awesome-ai")
            count += 1
    print(f"  → {count} prompts")


def main():
    if os.path.exists(PROMPTS_DIR):
        shutil.rmtree(PROMPTS_DIR)
    os.makedirs(PROMPTS_DIR)
    print(f"Output: {PROMPTS_DIR}")

    parse_nymbo()
    parse_moritz()
    parse_fka()
    parse_danielrosehill()
    parse_awesome_ai()

    total = sum(
        len([f for f in os.listdir(os.path.join(PROMPTS_DIR, cat)) if f.endswith(".md")])
        for cat in os.listdir(PROMPTS_DIR)
        if os.path.isdir(os.path.join(PROMPTS_DIR, cat))
    )
    print(f"\nTotal: {total} prompts")
    for cat in sorted(os.listdir(PROMPTS_DIR)):
        cat_dir = os.path.join(PROMPTS_DIR, cat)
        if os.path.isdir(cat_dir):
            n = len([f for f in os.listdir(cat_dir) if f.endswith(".md")])
            print(f"  {cat:<15} {n}")


if __name__ == "__main__":
    main()
