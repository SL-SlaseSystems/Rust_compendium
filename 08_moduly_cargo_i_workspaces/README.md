[← Spis treści](../README.md)

# 8. Moduły, Cargo i workspaces

## Dla kogo i po co

Dla osób organizujących kod większy niż pojedynczy plik oraz zarządzających zależnościami, konfiguracją i publikowaniem crate'ów.

## Wymagania wstępne

Podstawy języka i doświadczenie z małym projektem Cargo.

## Kolejność materiałów

1. [Moduły, ścieżki i widoczność](01_moduly_sciezki_i_widocznosc.md)
2. [Crates, pakiety i workspaces](02_crates_pakiety_i_workspaces.md)
3. [Zależności, features i `cfg`](03_zaleznosci_features_i_cfg.md)
4. [Profile, build scripts i publikowanie](04_profile_build_scripts_i_publikowanie.md)
5. [Nightly, unstable i feature gates](05_nightly_unstable_i_feature_gates.md)

## Po tym dziale

Umiesz podzielić projekt na stabilne granice, kontrolować features i przygotować bibliotekę do publikacji.

## Praca z rozdziałami

Każdy rozdział zawiera model działania, przykłady, diagnostykę, decyzje produkcyjne i trzy zadania o rosnącym poziomie trudności. Najpierw przewiduj wynik kodu, następnie go uruchom, a dopiero potem porównaj rozwiązanie.

- [Moduły, ścieżki i widoczność: rozwiązania](../rozwiazania/08_moduly_cargo_i_workspaces/01_moduly_sciezki_i_widocznosc.md)
- [Crates, pakiety i workspaces: rozwiązania](../rozwiazania/08_moduly_cargo_i_workspaces/02_crates_pakiety_i_workspaces.md)
- [Zależności, features i `cfg`: rozwiązania](../rozwiazania/08_moduly_cargo_i_workspaces/03_zaleznosci_features_i_cfg.md)
- [Profile, build scripts i publikowanie: rozwiązania](../rozwiazania/08_moduly_cargo_i_workspaces/04_profile_build_scripts_i_publikowanie.md)
- [Nightly, unstable i feature gates: rozwiązania](../rozwiazania/08_moduly_cargo_i_workspaces/05_nightly_unstable_i_feature_gates.md)

Przykłady samowystarczalne odnoszą się do Rust 1.90, Edition 2024. Bloki `text` z zależnościami zewnętrznymi lub wymaganiami środowiskowymi opisują oddzielny kontrakt; nie są testami wykonanymi przez rustdoc.

## Co dalej

Przejdź do dokumentacji i testowania. Nightly traktuj jako świadomy koszt utrzymania, a nie standardowy etap nauki.
