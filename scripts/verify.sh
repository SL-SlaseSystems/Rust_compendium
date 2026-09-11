#!/bin/sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
content_list=$(mktemp)
trap 'rm -f "$content_list"' EXIT HUP INT TERM

python3 "$project_root/scripts/verify_content.py" "$project_root"

find "$project_root" -type f -name '*.md' \
    -not -path "$project_root/.git/*" \
    -not -path "$project_root/target/*" \
    -not -path "$project_root/.superpowers/*" \
    -not -path "$project_root/docs/superpowers/*" \
    -print | sort > "$content_list"

if command -v rustdoc >/dev/null 2>&1; then
    echo "Sprawdzanie przykładów przez $(rustdoc --version)"
    while IFS= read -r file; do
        if [ "$file" = "$project_root/150-zaawansowanych-mechanizmow-rust.md" ]; then
            echo "Pominięto rustdoc dla 150-zaawansowanych-mechanizmow-rust.md: wykonywalne przykłady czekają na dedykowany etap atlasu." >&2
            continue
        fi
        if grep -Eq '^(```|~~~)(rust|compile_fail|no_run|should_panic)' "$file"; then
            rustdoc --test --edition 2024 "$file"
        fi
    done < "$content_list"
else
    echo "Pominięto testy kodu: rustdoc nie jest dostępny." >&2
fi

echo "Weryfikacja zakończona pomyślnie."
