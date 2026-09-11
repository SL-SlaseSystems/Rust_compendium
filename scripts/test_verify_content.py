from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

from scripts.verify_content import discover_markdown, validate_markdown


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class MarkdownFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name).resolve()
        self.write("README.md", "# Kompendium\n")

    def write(self, relative_path: str, content: str) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
        return path

    def write_valid_expanded_chapter(self) -> Path:
        self.write(
            "rozwiazania/ownership.md",
            """
            [← Spis treści](../README.md)

            # Rozwiązania

            ## O02-1

            Rozwiązanie ćwiczenia.
            """,
        )
        return self.write(
            "03_pamiec_i_wlasnosc/ownership.md",
            """
            [← Spis treści](../README.md)
            <!-- status: expanded -->

            # Ownership

            ## Cele

            Poznaj model własności.

            ## Model mentalny

            Wartość ma jednego właściciela.

            ```rust
            fn main() {
                let value = String::from("Rust");
                assert_eq!(value, "Rust");
            }
            ```

            ## Diagnostyka kompilatora

            Czytaj pierwszą przyczynę błędu.

            ## Praktyka produkcyjna

            Przenoś własność świadomie.

            ## Sprawdź, czy rozumiesz

            Kto jest właścicielem wartości?

            ## Ćwiczenia

            - `O02-1` — podstawowe: wykonaj zadanie i zobacz [rozwiązanie](../rozwiazania/ownership.md#o02-1).

            ## Powiązane tematy

            - [Spis treści](../README.md)
            """,
        )


class ValidateMarkdownTests(MarkdownFixture):
    def test_accepts_valid_expanded_chapter(self) -> None:
        self.write_valid_expanded_chapter()

        problems = validate_markdown(self.root, discover_markdown(self.root))

        self.assertEqual(problems, [])

    def test_reports_unclosed_fence(self) -> None:
        self.write(
            "chapter/broken.md",
            """
            [← Spis treści](../README.md)

            # Broken

            ```rust
            fn main() {}
            """,
        )

        problems = validate_markdown(self.root, discover_markdown(self.root))

        self.assertTrue(any("niedomknięty blok kodu" in problem for problem in problems))

    def test_reports_dead_relative_link(self) -> None:
        self.write(
            "chapter/dead-link.md",
            """
            [← Spis treści](../README.md)

            # Martwy link

            [Brakujący plik](missing.md)
            """,
        )

        problems = validate_markdown(self.root, discover_markdown(self.root))

        self.assertTrue(any("brak celu linku: missing.md" in problem for problem in problems))

    def test_reports_wrong_first_link(self) -> None:
        self.write(
            "chapter/wrong-backlink.md",
            """
            # Bez odsyłacza

            Treść.
            """,
        )

        problems = validate_markdown(self.root, discover_markdown(self.root))

        self.assertTrue(
            any("brak linku powrotnego na początku" in problem for problem in problems)
        )

    def test_reports_expanded_marker_without_exercises_section(self) -> None:
        chapter = self.write_valid_expanded_chapter()
        chapter.write_text(
            chapter.read_text(encoding="utf-8").replace("## Ćwiczenia", "## Zadania"),
            encoding="utf-8",
        )

        problems = validate_markdown(self.root, discover_markdown(self.root))

        self.assertTrue(any("brak wymaganej sekcji: ## Ćwiczenia" in p for p in problems))

    def test_reports_exercise_without_solution_link(self) -> None:
        chapter = self.write_valid_expanded_chapter()
        chapter.write_text(
            chapter.read_text(encoding="utf-8").replace(
                "wykonaj zadanie i zobacz [rozwiązanie](../rozwiazania/ownership.md#o02-1)",
                "wykonaj zadanie samodzielnie",
            ),
            encoding="utf-8",
        )

        problems = validate_markdown(self.root, discover_markdown(self.root))

        self.assertTrue(any("O02-1: brak linku do rozwiązania" in p for p in problems))

    def test_reports_solution_without_matching_anchor(self) -> None:
        self.write_valid_expanded_chapter()
        solution = self.root / "rozwiazania/ownership.md"
        solution.write_text(
            solution.read_text(encoding="utf-8").replace("## O02-1", "## O02-2"),
            encoding="utf-8",
        )

        problems = validate_markdown(self.root, discover_markdown(self.root))

        self.assertTrue(any("O02-1: brak identycznej kotwicy w rozwiązaniu" in p for p in problems))

    def test_reports_duplicate_exercise_identifier(self) -> None:
        chapter = self.write_valid_expanded_chapter()
        duplicate = chapter.read_text(encoding="utf-8").replace(
            "# Ownership", "# Ownership — powtórzenie"
        )
        self.write("03_pamiec_i_wlasnosc/ownership-copy.md", duplicate)

        problems = validate_markdown(self.root, discover_markdown(self.root))

        self.assertTrue(any("zduplikowany identyfikator ćwiczenia: O02-1" in p for p in problems))

    def test_ignores_markdown_links_inside_code_fences(self) -> None:
        self.write(
            "chapter/code-link.md",
            """
            [← Spis treści](../README.md)

            # Przykład tekstu

            ```text
            [To nie jest odsyłacz](missing.md)
            ```
            """,
        )

        problems = validate_markdown(self.root, discover_markdown(self.root))

        self.assertEqual(problems, [])

    def test_ignores_expanded_marker_inside_code_fences(self) -> None:
        self.write(
            "chapter/documented-marker.md",
            """
            [← Spis treści](../README.md)

            # Dokumentacja znacznika

            ```markdown
            <!-- status: expanded -->
            ```
            """,
        )

        problems = validate_markdown(self.root, discover_markdown(self.root))

        self.assertEqual(problems, [])


class DiscoverMarkdownTests(MarkdownFixture):
    def test_excludes_generated_and_build_directories(self) -> None:
        self.write("chapter/kept.md", "# Treść\n")
        self.write(".git/internal.md", "# Git\n")
        self.write("target/generated.md", "# Target\n")
        self.write("docs/superpowers/plan.md", "# Plan\n")
        self.write(".superpowers/sdd/brief.md", "# Stan koordynacji\n")

        discovered = [path.relative_to(self.root).as_posix() for path in discover_markdown(self.root)]

        self.assertEqual(discovered, ["README.md", "chapter/kept.md"])


class CliTests(MarkdownFixture):
    def test_cli_returns_zero_for_valid_content_and_one_for_invalid_content(self) -> None:
        self.write_valid_expanded_chapter()
        valid = subprocess.run(
            ["python3", str(PROJECT_ROOT / "scripts/verify_content.py"), str(self.root)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.write("chapter/invalid.md", "# Bez linku powrotnego\n")
        invalid = subprocess.run(
            ["python3", str(PROJECT_ROOT / "scripts/verify_content.py"), str(self.root)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(valid.returncode, 0, valid.stderr)
        self.assertEqual(invalid.returncode, 1)
        self.assertIn("brak linku powrotnego na początku", invalid.stderr)


class VerifyWrapperTests(MarkdownFixture):
    def test_skips_only_atlas_rustdoc_and_keeps_chapters_and_solutions(self) -> None:
        scripts = self.root / "scripts"
        scripts.mkdir()
        shutil.copy2(PROJECT_ROOT / "scripts/verify.sh", scripts / "verify.sh")
        shutil.copy2(
            PROJECT_ROOT / "scripts/verify_content.py", scripts / "verify_content.py"
        )
        self.write(
            "chapter/regular.md",
            """
            [← Spis treści](../README.md)

            # Zwykły rozdział

            ```rust
            fn main() {}
            ```
            """,
        )
        self.write(
            "rozwiazania/regular.md",
            """
            [← Spis treści](../README.md)

            # Rozwiązanie

            ```rust
            fn main() {}
            ```
            """,
        )
        self.write(
            "150-zaawansowanych-mechanizmow-rust.md",
            """
            # Atlas

            ```rust
            fn main() {}
            ```
            """,
        )
        bin_directory = self.root / "bin"
        bin_directory.mkdir()
        fake_rustdoc = bin_directory / "rustdoc"
        fake_rustdoc.write_text(
            """#!/bin/sh
if [ "${1-}" = "--version" ]; then
    echo "rustdoc fake"
    exit 0
fi
printf '%s\\n' "$*" >> "$RUSTDOC_LOG"
""",
            encoding="utf-8",
        )
        fake_rustdoc.chmod(0o755)
        rustdoc_log = self.root / "rustdoc.log"
        environment = os.environ.copy()
        environment["PATH"] = f"{bin_directory}:{environment['PATH']}"
        environment["RUSTDOC_LOG"] = str(rustdoc_log)

        result = subprocess.run(
            ["bash", str(scripts / "verify.sh")],
            cwd=self.root,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        rustdoc_calls = rustdoc_log.read_text(encoding="utf-8")
        self.assertIn("chapter/regular.md", rustdoc_calls)
        self.assertIn("rozwiazania/regular.md", rustdoc_calls)
        self.assertNotIn("150-zaawansowanych-mechanizmow-rust.md", rustdoc_calls)
        self.assertIn("150-zaawansowanych-mechanizmow-rust.md", result.stderr)
        self.assertIn("wykonywalne przykłady czekają na dedykowany etap atlasu", result.stderr)


if __name__ == "__main__":
    unittest.main()
