#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote


EXPANDED_MARKER = "<!-- status: expanded -->"
REQUIRED_SECTIONS = (
    "## Cele",
    "## Diagnostyka kompilatora",
    "## Praktyka produkcyjna",
    "## Sprawdź, czy rozumiesz",
    "## Ćwiczenia",
    "## Powiązane tematy",
)
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
FENCE_PATTERN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
EXERCISE_ID_PATTERN = re.compile(r"`([A-Z]\d{2}-\d+)`")
LIST_ITEM_PATTERN = re.compile(r"^([ \t]*)([-+*]|\d{1,9}[.)])([ \t]+)")


def discover_markdown(root: Path) -> list[Path]:
    """Return repository Markdown files, excluding VCS and generated state."""
    root = root.resolve()
    discovered: list[Path] = []
    for path in root.rglob("*.md"):
        if not path.is_file():
            continue
        parts = path.relative_to(root).parts
        if ".git" in parts or "target" in parts or ".superpowers" in parts:
            continue
        if len(parts) >= 2 and parts[:2] == ("docs", "superpowers"):
            continue
        discovered.append(path)
    return sorted(discovered)


def _indent_width(text: str) -> int:
    width = 0
    for character in text:
        if character == " ":
            width += 1
        elif character == "\t":
            width += 4 - width % 4
        else:
            break
    return width


def _outside_fences(lines: list[str]) -> tuple[list[str], bool, bool]:
    outside: list[str] = []
    fence_character = ""
    fence_length = 0
    has_rust_fence = False
    list_content_indents: list[int] = []

    for line in lines:
        match = FENCE_PATTERN.match(line)
        if match:
            marker, info = match.groups()
            if not fence_character:
                fence_character = marker[0]
                fence_length = len(marker)
                has_rust_fence |= info.strip().split(",", 1)[0] == "rust"
            elif marker[0] == fence_character and len(marker) >= fence_length:
                fence_character = ""
                fence_length = 0
            continue
        if fence_character:
            continue
        if not line.strip():
            outside.append(line)
            continue

        indentation = _indent_width(line)
        while list_content_indents and indentation < list_content_indents[-1]:
            list_content_indents.pop()
        code_base = list_content_indents[-1] if list_content_indents else 0
        if indentation >= code_base + 4:
            continue

        outside.append(line)
        list_item = LIST_ITEM_PATTERN.match(line)
        if list_item:
            prefix, marker, spacing = list_item.groups()
            content_indent = _indent_width(prefix) + len(marker) + len(spacing)
            list_content_indents.append(content_indent)

    return outside, bool(fence_character), has_rust_fence


def _link_target(raw_target: str) -> tuple[str, str]:
    target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
    path, separator, fragment = target.partition("#")
    return unquote(path), unquote(fragment) if separator else ""


def _has_solution_anchor(path: Path, exercise_id: str, fragment: str) -> bool:
    if fragment != exercise_id.lower():
        return False
    lines = path.read_text(encoding="utf-8").splitlines()
    prose_lines, _, _ = _outside_fences(lines)
    heading = re.compile(rf"^ {{0,3}}#{{1,6}}[ \t]+{re.escape(exercise_id)}[ \t]*$")
    explicit_anchor = re.compile(
        rf"<(?:a|span)\s+[^>]*(?:id|name)=[\"']{re.escape(fragment)}[\"'][^>]*>",
        re.IGNORECASE,
    )
    return any(heading.match(line) or explicit_anchor.search(line) for line in prose_lines)


def validate_markdown(root: Path, files: list[Path]) -> list[str]:
    """Validate navigation, links and the expanded-chapter contract."""
    root = root.resolve()
    problems: list[str] = []
    exercise_locations: dict[str, Path] = {}

    for original_path in files:
        path = original_path.resolve()
        relative_path = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()

        if not text:
            problems.append(f"{relative_path}: pusty plik")

        outside_fences, has_unclosed_fence, has_rust_fence = _outside_fences(lines)
        if has_unclosed_fence:
            problems.append(f"{relative_path}: niedomknięty blok kodu")

        if path.parent != root and path.name != "README.md":
            first_nonempty = next((line for line in lines if line.strip()), "")
            depth = len(path.parent.relative_to(root).parts)
            backlink_target = "/".join([".."] * depth + ["README.md"])
            expected_backlink = f"[← Spis treści]({backlink_target})"
            if first_nonempty != expected_backlink:
                problems.append(f"{relative_path}: brak linku powrotnego na początku")

        outside_text = "\n".join(outside_fences)
        for raw_target in LINK_PATTERN.findall(outside_text):
            target, _ = _link_target(raw_target)
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                problems.append(f"{relative_path}: link wychodzi poza projekt: {target}")
                continue
            if not resolved.exists():
                problems.append(f"{relative_path}: brak celu linku: {target}")

        if EXPANDED_MARKER not in outside_fences:
            continue

        for section in REQUIRED_SECTIONS:
            if section not in outside_fences:
                problems.append(f"{relative_path}: brak wymaganej sekcji: {section}")
        if not any(
            re.match(r"^##\s+(?:Model|Reguły)(?:\s|$)", line, re.IGNORECASE)
            for line in outside_fences
        ):
            problems.append(f"{relative_path}: brak wymaganej sekcji modelu lub reguł")
        if not has_rust_fence:
            problems.append(f"{relative_path}: brak bloku rust")

        try:
            exercise_start = outside_fences.index("## Ćwiczenia") + 1
        except ValueError:
            continue
        exercise_lines: list[str] = []
        for line in outside_fences[exercise_start:]:
            if line.startswith("## "):
                break
            exercise_lines.append(line)

        for line in exercise_lines:
            for exercise_id in EXERCISE_ID_PATTERN.findall(line):
                if exercise_id in exercise_locations:
                    problems.append(
                        f"{relative_path}: zduplikowany identyfikator ćwiczenia: {exercise_id}"
                    )
                else:
                    exercise_locations[exercise_id] = path

                solution_links: list[tuple[Path, str]] = []
                for raw_target in LINK_PATTERN.findall(line):
                    target, fragment = _link_target(raw_target)
                    if not target:
                        continue
                    resolved = (path.parent / target).resolve()
                    try:
                        relative_target = resolved.relative_to(root)
                    except ValueError:
                        continue
                    if relative_target.parts and relative_target.parts[0] == "rozwiazania":
                        solution_links.append((resolved, fragment))

                if not solution_links:
                    problems.append(f"{relative_path}: {exercise_id}: brak linku do rozwiązania")
                    continue
                solution_path, fragment = solution_links[0]
                if not solution_path.is_file() or not _has_solution_anchor(
                    solution_path, exercise_id, fragment
                ):
                    problems.append(
                        f"{relative_path}: {exercise_id}: brak identycznej kotwicy w rozwiązaniu"
                    )

    return problems


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 1:
        print("Użycie: verify_content.py KATALOG_PROJEKTU", file=sys.stderr)
        return 1
    root = Path(arguments[0])
    files = discover_markdown(root)
    if not files:
        print("Brak plików Markdown.", file=sys.stderr)
        return 1
    problems = validate_markdown(root, files)
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
