#!/usr/bin/env python3
from __future__ import annotations

import json
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
EXPECTED_SECTION_DIRS = (
    "01_wprowadzenie_i_toolchain",
    "02_podstawy_jezyka",
    "03_ownership_i_pamiec",
    "04_struktury_enumy_i_wzorce",
    "05_generics_traits_i_system_typow",
    "06_kolekcje_iteratory_i_closures",
    "07_obsluga_bledow",
    "08_moduly_cargo_i_workspaces",
    "09_dokumentacja_testowanie_i_jakosc",
    "10_wspolbieznosc",
    "11_async_rust",
    "12_makra",
    "13_io_siec_i_protokoly",
    "14_idiomy_wzorce_i_architektura",
    "15_aplikacje_cli",
    "16_web_i_api",
    "17_bazy_danych_i_persystencja",
    "18_serializacja_konfiguracja_i_integracje",
    "19_runtime_pamiec_i_kompilator",
    "20_wydajnosc_i_optymalizacja",
    "21_unsafe_soundness_i_model_pamieci",
    "22_ffi_i_interoperacyjnosc",
    "23_no_std_allocatory_i_embedded",
    "24_wasm_i_wieloplatformowosc",
    "25_debugowanie_i_utrzymanie",
    "26_testowanie_zaawansowane_fuzzing_i_miri",
    "27_bezpieczenstwo_aplikacji",
    "28_ci_cd_i_release_engineering",
    "29_observability_i_produkcja",
    "30_projekty_przekrojowe",
)
LEGACY_SECTION_DIRS = (
    "01_wprowadzenie",
    "02_podstawy_jezyka",
    "03_pamiec_i_wlasnosc",
    "04_typy_i_modelowanie",
    "05_kolekcje_i_iteratory",
    "06_bledy",
    "07_moduly_i_cargo",
    "08_testowanie_i_jakosc",
    "09_wspolbieznosc",
    "10_async",
    "11_makra",
    "12_systemy_i_interoperacyjnosc",
    "13_wzorce_i_architektura",
    "zaawansowane",
    "rozwiazania/01_wprowadzenie",
)
MIGRATION_MANIFEST_PATH = Path(
    "docs/superpowers/audits/2026-10-04-mapa-migracji-30-dzialow.json"
)


def discover_markdown(root: Path) -> list[Path]:
    """Return repository Markdown files, excluding VCS and generated state."""
    root = root.resolve()
    discovered: list[Path] = []
    for path in root.rglob("*.md"):
        if not path.is_file():
            continue
        parts = path.relative_to(root).parts
        if any(
            excluded in parts
            for excluded in (".git", ".worktrees", "target", ".superpowers")
        ):
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


def _strip_indent(text: str, width: int) -> str:
    index = 0
    removed = 0
    while index < len(text) and removed < width:
        character = text[index]
        if character == " ":
            removed += 1
        elif character == "\t":
            next_tab_stop = removed + 4 - removed % 4
            if next_tab_stop > width:
                return " " * (next_tab_stop - width) + text[index + 1 :]
            removed = next_tab_stop
        else:
            break
        index += 1
    return text[index:]


def _outside_fences(lines: list[str]) -> tuple[list[str], bool, bool]:
    outside: list[str] = []
    fence_character = ""
    fence_length = 0
    fence_container_indent = 0
    has_rust_fence = False
    list_content_indents: list[int] = []

    for line in lines:
        if fence_character:
            match = FENCE_PATTERN.match(_strip_indent(line, fence_container_indent))
            if match:
                marker, _ = match.groups()
                if marker[0] == fence_character and len(marker) >= fence_length:
                    fence_character = ""
                    fence_length = 0
                    fence_container_indent = 0
            continue
        if not line.strip():
            outside.append(line)
            continue

        indentation = _indent_width(line)
        while list_content_indents and indentation < list_content_indents[-1]:
            list_content_indents.pop()
        code_base = list_content_indents[-1] if list_content_indents else 0

        match = FENCE_PATTERN.match(_strip_indent(line, code_base))
        if match:
            marker, info = match.groups()
            fence_character = marker[0]
            fence_length = len(marker)
            fence_container_indent = code_base
            has_rust_fence |= info.strip().split(",", 1)[0] == "rust"
            continue
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


def validate_section_structure(root: Path) -> list[str]:
    """Validate the canonical section directories and root navigation."""
    root = root.resolve()
    problems: list[str] = []
    root_readme = root / "README.md"
    root_text = root_readme.read_text(encoding="utf-8") if root_readme.is_file() else ""
    navigation_targets = {
        _link_target(raw_target)[0] for raw_target in LINK_PATTERN.findall(root_text)
    }

    for section in EXPECTED_SECTION_DIRS:
        readme_target = f"{section}/README.md"
        if not (root / readme_target).is_file():
            problems.append(f"brak README działu: {readme_target}")
        if readme_target not in navigation_targets:
            problems.append(f"README.md: brak linku do działu: {readme_target}")

    if (root / "zaawansowane").exists():
        problems.append("stary katalog nadal istnieje: zaawansowane/")

    return problems


def load_migration_manifest(path: Path) -> list[dict[str, str]]:
    """Load and validate the versioned content-migration manifest."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{path}: niepoprawny manifest: {error}") from error

    if not isinstance(document, dict) or document.get("version") != 1:
        raise ValueError(f"{path}: nieobsługiwana wersja manifestu")
    moves = document.get("moves")
    if not isinstance(moves, list):
        raise ValueError(f"{path}: pole moves musi być listą")

    entries: list[dict[str, str]] = []
    for index, entry in enumerate(moves):
        if not isinstance(entry, dict) or any(
            not isinstance(entry.get(field), str)
            for field in ("source", "destination", "disposition")
        ):
            raise ValueError(f"{path}: niepoprawny wpis migracji nr {index + 1}")
        entries.append(
            {
                "source": entry["source"],
                "destination": entry["destination"],
                "disposition": entry["disposition"],
            }
        )
    return entries


def validate_migration_manifest(
    root: Path, entries: list[dict[str, str]]
) -> list[str]:
    """Validate migration uniqueness, coverage and filesystem completion."""
    root = root.resolve()
    problems: list[str] = []
    sources: set[str] = set()
    move_destinations: set[str] = set()

    for entry in entries:
        source = entry.get("source", "")
        destination = entry.get("destination", "")
        disposition = entry.get("disposition", "")

        if disposition not in {"move", "merge"}:
            problems.append(f"nieznany sposób migracji: {disposition or '<pusty>'}")
        if source in sources:
            problems.append(f"zduplikowane źródło migracji: {source}")
        else:
            sources.add(source)
        if disposition == "move":
            if destination in move_destinations:
                problems.append(f"zduplikowany cel migracji: {destination}")
            else:
                move_destinations.add(destination)

        source_path = root / source
        destination_path = root / destination
        if source != destination and source_path.exists():
            problems.append(f"źródło nadal istnieje po migracji: {source}")
        if not destination_path.exists():
            problems.append(f"brak celu migracji: {destination}")

    for directory in LEGACY_SECTION_DIRS:
        legacy_root = root / directory
        if not legacy_root.is_dir():
            continue
        for path in sorted(legacy_root.rglob("*.md")):
            relative_path = path.relative_to(root).as_posix()
            if directory in EXPECTED_SECTION_DIRS and path == legacy_root / "README.md":
                continue
            if relative_path not in sources:
                problems.append(f"brak wpisu migracji dla: {relative_path}")

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
    problems.extend(validate_section_structure(root))
    manifest_path = root / MIGRATION_MANIFEST_PATH
    if manifest_path.is_file():
        try:
            entries = load_migration_manifest(manifest_path)
        except ValueError as error:
            problems.append(str(error))
        else:
            problems.extend(validate_migration_manifest(root, entries))
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
