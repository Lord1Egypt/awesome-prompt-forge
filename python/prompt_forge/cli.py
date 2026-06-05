#!/usr/bin/env python3
"""Command-line interface for awesome-prompt-forge."""

import argparse
import sys
from .loader import load, search, list_prompts, categories


def main():
    parser = argparse.ArgumentParser(
        prog="promptforge",
        description="awesome-prompt-forge — 350+ lazy-loading AI system prompts"
    )
    sub = parser.add_subparsers(dest="command")

    p_load = sub.add_parser("load", help="Load and print a prompt")
    p_load.add_argument("name")
    p_load.add_argument("--category", "-c", default=None)

    p_search = sub.add_parser("search", help="Search prompts")
    p_search.add_argument("query")
    p_search.add_argument("--category", "-c", default=None)
    p_search.add_argument("--limit", "-n", type=int, default=10)

    p_list = sub.add_parser("list", help="List all prompts")
    p_list.add_argument("--category", "-c", default=None)

    sub.add_parser("stats", help="Show prompt counts per category")

    args = parser.parse_args()

    if args.command == "load":
        try:
            p = load(args.name, args.category)
            print(f"# {p.name} [{p.category}]\n")
            print(p.content)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "search":
        results = search(args.query, args.category, args.limit)
        if not results:
            print(f"No prompts found for '{args.query}'")
        for r in results:
            print(f"[{r['category']:12}] {r['name']}")
            if r["description"]:
                print(f"              {r['description'][:80]}")
            print()

    elif args.command == "list":
        prompts = list_prompts(args.category)
        for p in prompts:
            print(f"[{p['category']:12}] {p['name']}")

    elif args.command == "stats":
        stats = categories()
        for k, v in stats.items():
            print(f"  {k:<15} {v}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
