[← Spis treści](../../README.md)

# Rozwiązania: Miri, sanitizery i modelowanie współbieżności

[Rozdział źródłowy](../../26_testowanie_zaawansowane_fuzzing_i_miri/02_miri_sanitizery_i_loom.md)

## D06-1

Niepusty slice zapewnia ważny pierwszy element, jego inicjalizację i wyrównanie; referencja utrzymuje alokację przy życiu i zakazuje nielegalnej mutacji. Odczyt `u32` nie przejmuje zasobu. Dla pustego wejścia zwracamy przed odczytem.

## D06-2

FFI: odpowiednio zbudowany sanitizer całej ścieżki, z uwzględnieniem obcego kodu. Aliasing w małym module Rust: Miri oraz przegląd kontraktu. Utracona aktualizacja: test niezmiennika i model Loom; atomowość pojedynczych load/store nie oznacza atomowej operacji złożonej.

## D06-3

Dwa wątki odczytują długość, porównują z limitem i próbują dodać element. Asercja mówi, że długość nie przekracza limitu. Model powinien dopuścić przeplot między sprawdzeniem a dodaniem. Naprawa obejmuje jedną sekcję krytyczną dla obu kroków albo udowodniony atomowy protokół rezerwacji; sam atomiczny licznik nie uzasadnia poprawności.
