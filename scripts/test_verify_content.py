from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

from scripts.verify_content import (
    discover_markdown,
    load_migration_manifest,
    validate_markdown,
    validate_migration_manifest,
    validate_section_structure,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SECTION_DIRS_FOR_TEST = (
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

    def write_valid_section_structure(self) -> None:
        navigation = ["# Kompendium", ""]
        for section in EXPECTED_SECTION_DIRS_FOR_TEST:
            self.write(f"{section}/README.md", f"# {section}\n")
            navigation.append(f"- [{section}]({section}/README.md)")
        self.write("README.md", "\n".join(navigation))


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

    def test_accepts_root_backlink_from_nested_solution(self) -> None:
        self.write(
            "rozwiazania/03_pamiec_i_wlasnosc/ownership.md",
            """
            [← Spis treści](../../README.md)

            # Rozwiązania ownership
            """,
        )

        problems = validate_markdown(self.root, discover_markdown(self.root))

        self.assertEqual(problems, [])

    def test_rejects_wrong_root_backlink_from_nested_solution(self) -> None:
        self.write(
            "rozwiazania/03_pamiec_i_wlasnosc/ownership.md",
            """
            [← Spis treści](../README.md)

            # Rozwiązania ownership
            """,
        )

        problems = validate_markdown(self.root, discover_markdown(self.root))

        self.assertTrue(
            any("brak linku powrotnego na początku" in problem for problem in problems)
        )
        self.assertTrue(any("brak celu linku: ../README.md" in p for p in problems))

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

    def test_rejects_solution_anchor_inside_fenced_code_block(self) -> None:
        self.write_valid_expanded_chapter()
        self.write(
            "rozwiazania/ownership.md",
            """
            [← Spis treści](../README.md)

            # Rozwiązania

            ```text
            <a id="o02-1"></a>
            ```
            """,
        )

        problems = validate_markdown(self.root, discover_markdown(self.root))

        self.assertTrue(any("O02-1: brak identycznej kotwicy w rozwiązaniu" in p for p in problems))

    def test_rejects_solution_anchor_inside_indented_code_block(self) -> None:
        self.write_valid_expanded_chapter()
        self.write(
            "rozwiazania/ownership.md",
            """
            [← Spis treści](../README.md)

            # Rozwiązania

                ## O02-1
            """,
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

    def test_ignores_markdown_links_inside_indented_code_blocks(self) -> None:
        self.write(
            "chapter/indented-code-link.md",
            """
            [← Spis treści](../README.md)

            # Przykład tekstu

                [To nie jest odsyłacz](missing.md)
            """,
        )

        problems = validate_markdown(self.root, discover_markdown(self.root))

        self.assertEqual(problems, [])

    def test_validates_markdown_links_in_nested_list_content(self) -> None:
        self.write(
            "chapter/nested-list-link.md",
            """
            [← Spis treści](../README.md)

            # Lista

            - Materiały:
                - [Brakujący materiał](missing.md)
            """,
        )

        problems = validate_markdown(self.root, discover_markdown(self.root))

        self.assertTrue(any("brak celu linku: missing.md" in p for p in problems))

    def test_ignores_links_inside_fenced_code_nested_in_list(self) -> None:
        self.write(
            "chapter/list-fenced-code-link.md",
            """
            [← Spis treści](../README.md)

            # Lista z kodem

            - Przykład:
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
    def test_excludes_managed_worktrees(self) -> None:
        self.write(".worktrees/feature/chapter.md", "# Kopia z worktree\n")

        discovered = [path.relative_to(self.root).as_posix() for path in discover_markdown(self.root)]

        self.assertEqual(discovered, ["README.md"])

    def test_excludes_generated_and_build_directories(self) -> None:
        self.write("chapter/kept.md", "# Treść\n")
        self.write(".git/internal.md", "# Git\n")
        self.write("target/generated.md", "# Target\n")
        self.write("docs/superpowers/plan.md", "# Plan\n")
        self.write(".superpowers/sdd/brief.md", "# Stan koordynacji\n")

        discovered = [path.relative_to(self.root).as_posix() for path in discover_markdown(self.root)]

        self.assertEqual(discovered, ["README.md", "chapter/kept.md"])


class ValidateSectionStructureTests(MarkdownFixture):
    def test_reports_missing_section_readmes(self) -> None:
        self.write("README.md", "")

        problems = validate_section_structure(self.root)

        self.assertIn(
            "brak README działu: 01_wprowadzenie_i_toolchain/README.md",
            problems,
        )
        self.assertIn(
            "brak README działu: 30_projekty_przekrojowe/README.md",
            problems,
        )

    def test_reports_section_missing_from_root_navigation(self) -> None:
        navigation: list[str] = ["# Kompendium", ""]
        for section in EXPECTED_SECTION_DIRS_FOR_TEST:
            self.write(f"{section}/README.md", f"# {section}\n")
            if section != "17_bazy_danych_i_persystencja":
                navigation.append(f"- [{section}]({section}/README.md)")
        self.write("README.md", "\n".join(navigation))

        problems = validate_section_structure(self.root)

        self.assertEqual(
            problems,
            [
                "README.md: brak linku do działu: "
                "17_bazy_danych_i_persystencja/README.md"
            ],
        )


class MigrationManifestTests(MarkdownFixture):
    def test_allows_new_map_in_unchanged_section(self) -> None:
        self.write("02_podstawy_jezyka/README.md", "# Mapa nowego działu\n")

        problems = validate_migration_manifest(self.root, [])

        self.assertEqual(problems, [])

    def test_reports_duplicate_missing_target_and_unmapped_legacy_file(self) -> None:
        self.write("01_wprowadzenie/source.md", "# Źródło\n")
        self.write("01_wprowadzenie/orphan.md", "# Pominięty plik\n")
        entries = [
            {
                "source": "01_wprowadzenie/source.md",
                "destination": "01_wprowadzenie_i_toolchain/source.md",
                "disposition": "move",
            },
            {
                "source": "01_wprowadzenie/source.md",
                "destination": "01_wprowadzenie_i_toolchain/duplicate.md",
                "disposition": "move",
            },
        ]

        problems = validate_migration_manifest(self.root, entries)

        self.assertTrue(any("zduplikowane źródło migracji" in p for p in problems))
        self.assertTrue(any("brak celu migracji" in p for p in problems))
        self.assertTrue(
            any("brak wpisu migracji dla: 01_wprowadzenie/orphan.md" in p for p in problems)
        )

    def test_load_rejects_unknown_manifest_version(self) -> None:
        manifest = self.write(
            "manifest.json",
            """
            {
              "version": 2,
              "moves": []
            }
            """,
        )

        with self.assertRaisesRegex(ValueError, "nieobsługiwana wersja manifestu"):
            load_migration_manifest(manifest)


class CliTests(MarkdownFixture):
    def test_cli_reports_unfinished_migration(self) -> None:
        self.write_valid_section_structure()
        self.write(
            "01_wprowadzenie/source.md",
            """
            [← Spis treści](../README.md)

            # Nieprzeniesiony materiał
            """,
        )
        self.write(
            "docs/superpowers/audits/2026-10-04-mapa-migracji-30-dzialow.json",
            """
            {
              "version": 1,
              "moves": [
                {
                  "source": "01_wprowadzenie/source.md",
                  "destination": "01_wprowadzenie_i_toolchain/README.md",
                  "disposition": "merge"
                }
              ]
            }
            """,
        )

        result = subprocess.run(
            ["python3", str(PROJECT_ROOT / "scripts/verify_content.py"), str(self.root)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("źródło nadal istnieje po migracji", result.stderr)

    def test_cli_returns_zero_for_valid_content_and_one_for_invalid_content(self) -> None:
        self.write_valid_expanded_chapter()
        self.write_valid_section_structure()
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
    def test_skips_managed_worktree_copies(self) -> None:
        self.write_valid_section_structure()
        scripts = self.root / "scripts"
        scripts.mkdir()
        shutil.copy2(PROJECT_ROOT / "scripts/verify.sh", scripts / "verify.sh")
        shutil.copy2(
            PROJECT_ROOT / "scripts/verify_content.py", scripts / "verify_content.py"
        )
        self.write(
            ".worktrees/feature/chapter.md",
            """
            # Kopia rozdziału z worktree

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
        self.assertFalse(rustdoc_log.exists())

    def test_runs_fences_indented_by_up_to_three_spaces_only(self) -> None:
        self.write_valid_section_structure()
        scripts = self.root / "scripts"
        scripts.mkdir()
        shutil.copy2(PROJECT_ROOT / "scripts/verify.sh", scripts / "verify.sh")
        shutil.copy2(
            PROJECT_ROOT / "scripts/verify_content.py", scripts / "verify_content.py"
        )
        self.write(
            "chapter/three-spaces.md",
            """
            [← Spis treści](../README.md)

            # Fence z trzema spacjami

               ```rust
               fn main() {}
               ```
            """,
        )
        self.write(
            "chapter/four-spaces.md",
            """
            [← Spis treści](../README.md)

            # Blok wcięty czterema spacjami

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
        rustdoc_calls = (
            rustdoc_log.read_text(encoding="utf-8") if rustdoc_log.exists() else ""
        )
        self.assertIn("chapter/three-spaces.md", rustdoc_calls)
        self.assertNotIn("chapter/four-spaces.md", rustdoc_calls)

    def test_skips_only_atlas_rustdoc_and_keeps_chapters_and_solutions(self) -> None:
        self.write_valid_section_structure()
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
