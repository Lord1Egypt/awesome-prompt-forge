#!/bin/bash
# Rebuild prompts + index, copy into packages, and publish

set -e
cd "$(dirname "$0")/.."

echo "=== awesome-prompt-forge deploy ==="

echo "→ Parsing sources..."
python3 scripts/parse_sources.py

echo "→ Building index..."
python3 scripts/build_index.py

echo "→ Copying into packages..."
cp -r prompts python/prompt_forge/
cp index.json python/prompt_forge/
cp -r prompts js/
cp index.json js/

echo "→ Building Python package..."
cd python && python -m build && cd ..

echo "→ Publishing to PyPI..."
python -m twine upload python/dist/* --username __token__ --password "$(cat ~/.skillforge_tokens | grep PYPI | cut -d= -f2)"

echo "→ Publishing to npm..."
cd js && npm publish && cd ..

echo "=== Done! ==="
