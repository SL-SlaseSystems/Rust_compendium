#!/bin/sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
content_list=$(mktemp)
trap 'rm -f "$content_list"' EXIT HUP INT TERM

find "$project_root" -type f -name '*.md' \
    -not -path "$project_root/.git/*" \
    -not -path "$project_root/docs/superpowers/*" \
    -print | sort > "$content_list"

if [ ! -s "$content_list" ]; then
    echo "Brak plików Markdown." >&2
    exit 1
fi

empty_files=$(while IFS= read -r file; do
    [ -s "$file" ] || printf '%s\n' "$file"
done < "$content_list")
if [ -n "$empty_files" ]; then
    echo "Puste pliki:" >&2
    printf '%s\n' "$empty_files" >&2
    exit 1
fi

python3 - "$project_root" "$content_list" <<'PY'
from pathlib import Path
from urllib.parse import unquote
import re
import sys

root = Path(sys.argv[1])
files = [Path(line) for line in Path(sys.argv[2]).read_text().splitlines()]
problems: list[str] = []
link_pattern = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")

for path in files:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    fence_count = sum(
        1 for line in lines if re.match(r"^\s*(```|~~~)", line)
    )
    if fence_count % 2:
        problems.append(f"{path.relative_to(root)}: niedomknięty blok kodu")

    if path.parent != root and path.name != "README.md":
        first_nonempty = next((line for line in text.splitlines() if line.strip()), "")
        if first_nonempty != "[← Spis treści](../README.md)":
            problems.append(f"{path.relative_to(root)}: brak linku powrotnego na początku")

    outside_fences: list[str] = []
    in_fence = False
    for line in lines:
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            continue
        if not in_fence:
            outside_fences.append(line)

    for raw_target in link_pattern.findall("\n".join(outside_fences)):
        target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
        if (
            not target
            or target.startswith(("#", "http://", "https://", "mailto:"))
        ):
            continue
        target = unquote(target.split("#", 1)[0])
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            problems.append(f"{path.relative_to(root)}: link wychodzi poza projekt: {target}")
            continue
        if not resolved.exists():
            problems.append(f"{path.relative_to(root)}: brak celu linku: {target}")

if problems:
    print("\n".join(problems), file=sys.stderr)
    raise SystemExit(1)
PY

if command -v rustdoc >/dev/null 2>&1; then
    echo "Sprawdzanie przykładów przez $(rustdoc --version)"
    while IFS= read -r file; do
        if grep -Eq '^(```|~~~)(rust|compile_fail|no_run|should_panic)' "$file"; then
            rustdoc --test --edition 2024 "$file"
        fi
    done < "$content_list"
else
    echo "Pominięto testy kodu: rustdoc nie jest dostępny." >&2
fi

echo "Weryfikacja zakończona pomyślnie."
