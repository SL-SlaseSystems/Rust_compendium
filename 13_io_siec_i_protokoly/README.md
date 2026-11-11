[← Spis treści](../README.md)

# 13. I/O, sieć i protokoły

## Dla kogo i po co

Dla osób budujących programy współpracujące z plikami, procesami, gniazdami i formatami przesyłanymi między systemami.

## Wymagania wstępne

Obsługa błędów, iteratory, moduły oraz — dla wariantów asynchronicznych — podstawy async Rust.

## Kolejność materiałów

1. [Pliki, I/O i procesy](01_pliki_io_i_procesy.md)
2. [Sieć i protokoły](02_siec_i_protokoly.md)

## Po tym dziale

Umiesz bezpiecznie zarządzać zasobami I/O, buforowaniem, częściowymi odczytami i granicami protokołu.

## Praca z rozdziałami

Każdy rozdział zawiera model działania, przykłady, diagnostykę, decyzje produkcyjne i trzy zadania o rosnącym poziomie trudności. Najpierw przewiduj wynik kodu, następnie go uruchom, a dopiero potem porównaj rozwiązanie.

- [Pliki, I/O i procesy: rozwiązania](../rozwiazania/13_io_siec_i_protokoly/01_pliki_io_i_procesy.md)
- [Sieć i protokoły: rozwiązania](../rozwiazania/13_io_siec_i_protokoly/02_siec_i_protokoly.md)

Przykłady samowystarczalne odnoszą się do Rust 1.90, Edition 2024. Bloki `text` z zależnościami zewnętrznymi lub wymaganiami środowiskowymi opisują oddzielny kontrakt; nie są testami wykonanymi przez rustdoc.

## Co dalej

Przejdź do aplikacji CLI, web/API lub integracji. Waliduj dane na granicy systemu i ustawiaj jawne limity zasobów.
