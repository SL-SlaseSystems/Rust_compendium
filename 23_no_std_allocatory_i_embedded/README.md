[← Spis treści](../README.md)

# 23. `no_std`, allocatory i embedded

## Dla kogo i po co

Dla osób pracujących bez pełnego środowiska systemowego, z niestandardową alokacją lub na mikrokontrolerach.

## Wymagania wstępne

Cargo, features, layout, `unsafe`, atomiki oraz podstawowa znajomość platformy docelowej.

## Kolejność materiałów

1. [Podstawy WebAssembly, `no_std` i embedded](01_wasm_no_std_i_embedded.md)
2. [`no_std`, allocatory i embedded — zaawansowane](02_no_std_allocatory_i_embedded.md)

Pierwszy materiał jest wspólnym wprowadzeniem do WebAssembly, `no_std` i embedded. W tej ścieżce skup się na częściach dotyczących `core`, `alloc` i ograniczonego środowiska; zagadnienia przeglądarkowe kontynuuj w dziale 24.

## Po tym dziale

Rozumiesz granicę `core`/`alloc`/`std`, wymagania środowiska uruchomieniowego i odpowiedzialność własnego allocatora.

## Co dalej

Dla WebAssembly przejdź do osobnej ścieżki wieloplatformowej. W embedded oprzyj dalszą naukę na HAL-u konkretnego układu i dokumentacji platformy.
