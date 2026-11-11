# Niezależny przegląd: produkcja, platformy i atlas

Data: 11 listopada 2026. Przegląd obejmuje 14 nowych rozdziałów działów 24–30, ich 14 plików rozwiązań i indeksy, wszystkie 150 pozycji atlasu, README, CONTRIBUTING, ściągę, słownik, dalszą naukę, rejestr źródeł oraz skrypty weryfikacji. Przeczytano plan `docs/superpowers/plans/2026-11-11-poglebienie-30-dzialow.md`, początkowy diff `/private/tmp/rust-root-review.diff` i pełną treść ocenianych rozdziałów. Dla wskazanych luk przeczytano także docelowe opracowania kanoniczne.

Przegląd był read-only względem treści i Git. Poprawki wdrożyli autorzy; recenzent ponownie przeczytał wyłącznie zgłoszone miejsca i ich uzupełnienia. Ten plik jest jedynym artefaktem zapisanym przez recenzenta.

## Werdykt końcowy

**Zakres ocenianej części jest zgodny z planem, a jakość po poprawkach pozwala ją zaakceptować. Brak otwartych uwag Critical, Important i Minor.** W pierwszym przebiegu znaleziono cztery uwagi Important i cztery Minor; wszystkie zamknięto przez kontrolę konkretnych zmian. Nie stwierdzono potrzeby implementowania lub wdrażania siedmiu aplikacji z działu 30: rozdział jawnie dostarcza specyfikacje projektów, a drugi rozdział kompletny rdzeń parsera.

Werdykt dotyczy przydzielonego zakresu, nie zastępuje niezależnych przeglądów działów 01–23 ani końcowej kontroli całego kompendium.

## Mocne strony

- Nowe rozdziały zawierają rzeczywiste modele i kontrakty, a nie same listy tematów. Ograniczenia wejścia, kolejki, deadline, własność zadań i skutki zdalne są opisywane jako osobne obowiązki.
- Ćwiczenia odnoszą się do przedstawionych przykładów; rozwiązania podają konkretne przypadki, oczekiwane wyniki albo decyzje projektowe. W ocenionych 42 zadaniach nie znaleziono istotnej sprzeczności zadania z rozwiązaniem.
- Materiały poprawnie rozdzielają kompilację, linkowanie, wykonanie i integrację. Test natywnego parsera nie jest przedstawiany jako test przeglądarki, WASI, alertowania czy bazy.
- Rozdziały bezpieczeństwa uwzględniają autoryzację zasobu, dekompresję, uprawnienia build scripts/proc macros, rotację i redakcję sekretów. Bezpieczeństwo pamięci nie jest utożsamiane z bezpieczeństwem aplikacji.
- Parser referencyjny ma spójną gramatykę, politykę duplikatów, granice zasobów, pożyczony wynik oraz wyraźnie nazwane ograniczenia adaptera i streamingu.

## Critical

Brak.

## Important — znalezione i zamknięte

### I1. C `abs` było błędnie deklarowane jako `safe`

**Miejsce:** `150-zaawansowanych-mechanizmow-rust.md:2470` w początkowym diffie, punkt 97. Poprawiona deklaracja znajduje się obecnie w `150-zaawansowanych-mechanizmow-rust.md:2483`.

**Problem:** `abs(c_int::MIN)` ma niereprezentowalny dodatni wynik. Deklaracja `safe fn abs` umożliwiała wywołanie naruszające kontrakt C z całkowicie bezpiecznego kodu Rust. Samo ABI i typ argumentu nie dowodzą bezpieczeństwa całej dziedziny. Kontrakt potwierdzono w [WG14 N3220, §7.24.6.1](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf); rozróżnienie safe/unsafe extern wyjaśnia [Edition Guide](https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html).

**Poprawka i status:** zamknięte. `abs` jest `unsafe`, ma warunek wykluczający MIN, a `checked_abs` odrzuca tę wartość przed wywołaniem. Asercje obejmują zwykły ujemny argument i MIN. Nie wykonywano celowo UB.

### I2. `close_fd` nie zapewniało własności zamykanego deskryptora

**Miejsce:** `150-zaawansowanych-mechanizmow-rust.md:2438` i `:2448` w początkowym diffie, punkt 96. Obecna neutralna reprezentacja jest w `150-zaawansowanych-mechanizmow-rust.md:2446`.

**Problem:** `FileDescriptor(c_int)` implementowało Copy/Clone, a bezpieczne `close_fd` zamykało numer bez dowodu ownership. Można było zamknąć zasób nadal należący do `File` albo użyć skopiowanego uchwytu po ponownym przydzieleniu jego numeru. Komentarz SAFETY dowodził wyłącznie zgodności ABI. [Dokumentacja std::io: I/O Safety](https://doc.rust-lang.org/std/io/#io-safety) wprost wymaga własności lub odpowiedniej pożyczki zasobu.

**Poprawka i status:** zamknięte. Demonstrację `repr(transparent)` zastąpiono neutralnym `Status(c_int)`; usunięto operację zamykania. Osobny akapit odsyła do `OwnedFd`/`BorrowedFd` i wyjaśnia obowiązek ownership.

### I3. Część nowych odsyłaczy atlasu nie prowadziła do pogłębionego omówienia mechanizmu

**Miejsce:** początkowo `150-zaawansowanych-mechanizmow-rust.md:1649` (66), `:2956` (114), `:3041` (117), `:3066` (118) i `:3100` (119).

**Problem:** docelowe rozdziały nie omawiały odpowiednio `poll_fn`, `spare_capacity_mut`, `array::from_fn`, `fill_buf`/`consume` oraz vectored I/O. Sam poprawny link „Pełne omówienie i ćwiczenia” nie domykał wymogu pogłębienia tych tematów; pozostawały one wyłącznie krótkimi wpisami atlasu.

**Poprawka i status:** zamknięte po przeczytaniu uzupełnień:

- `11_async_rust/02_executor_waker_i_poll.md:122`: stan closure, Pending/wake, ręczny test, fairness i porzucenie przegranej future;
- `21_unsafe_soundness_i_model_pamieci/03_layout_alignment_i_uninitialized_memory.md:93`: reserve, inicjalizacja, publikacja len, zasobowy String, częściowy wynik i panika Clone;
- `06_kolekcje_iteratory_i_closures/01_tablice_wektory_i_sekwencje.md:131`: indeksy, FnMut, zerowa długość, typ tablicy i skutki konstruktora; odsyłacz 117 poprawiono;
- `13_io_siec_i_protokoly/01_pliki_io_i_procesy.md:124`: okres pożyczki bufora, faktycznie zużyte bajty, krótkie porcje i ograniczony stan parsera;
- `13_io_siec_i_protokoly/01_pliki_io_i_procesy.md:146`: IoSlice/IoSliceMut, częściowy postęp między segmentami, Interrupted/WriteZero i brak gwarancji jednego syscall.

### I4. Atlas niesłusznie wykluczał wykrywanie data races przez Miri

**Miejsce:** `150-zaawansowanych-mechanizmow-rust.md:3735` w początkowym diffie; obecnie `:3766`, punkt 139.

**Problem:** zdanie negujące analizowanie wyścigów między wątkami fałszowało zakres narzędzia i mogło prowadzić do błędnego doboru kontroli. [README Miri](https://github.com/rust-lang/miri) wymienia detektor data races oraz ograniczoną emulację słabej pamięci.

**Poprawka i status:** zamknięte. Tekst opisuje wykrywanie data races w obsługiwanych wykonaniach i odróżnia je od wyczerpującego sprawdzenia wszystkich harmonogramów.

## Minor — znalezione i zamknięte

- **M1, `150-zaawansowanych-mechanizmow-rust.md:1970`, punkt 78:** sformułowanie „Acquire publikuje” odwracało role Release/Acquire. Obecnie opisuje synchronizację z odpowiednim zapisem Release. Zamknięte.
- **M2, `150-zaawansowanych-mechanizmow-rust.md:2060`, punkt 81:** wariant square rozwijał wyrażenie argumentu dwukrotnie, więc efekt uboczny wykonywał się dwukrotnie. Dodano lokalny binding i asercję z licznikiem; autor potwierdził porażkę testu przed zmianą i sukces po niej. Zamknięte.
- **M3, początkowo `150-zaawansowanych-mechanizmow-rust.md:3742`, punkt 139:** komentarz obiecywał wiele wariantów losowego wykonania, choć komenda ustawiała tylko dodatkowe kontrole. Obecnie oddzielono pojedynczy przebieg i `-Zmiri-many-seeds=0..16` (`:3778`). Zamknięte.
- **M4, początkowo `150-zaawansowanych-mechanizmow-rust.md:2468`, punkt 97:** linkowanie biblioteki `c` wymagało nazwania środowiska. Obecnie akapit `:2472` wskazuje lokalnie wykonany Unix/macOS, a `cfg(unix)` jawnie pomija integrację na innych platformach. Nie przedstawia tego jako testu Windows/Wasm. Zamknięte.

## Dowody i granice weryfikacji

Stan przekazany do pierwszego przeglądu obejmował 597 zaliczonych testów pełnego verify, 126 doctestów atlasu oraz 29 testów walidatora. Nie powtarzano tych samych przebiegów bez nowej hipotezy. Po poprawkach koordynator potwierdził ponownie 126 doctestów atlasu oraz 13 doctestów trzech uzupełnionych plików 06/01, 11/02 i 13/01. Autor uzupełnienia 114 potwierdził siedem doctestów zmienionych przez siebie plików i osobny test paniki Clone z licznikiem Drop. Są to wyniki wykonawców, odrębne od wykonanej tutaj kontroli merytorycznej.

Świadomie nie wykonywano poniższych zachowań; ich opisane kontrakty i ograniczenia były oceniane:

- Ładowania Wasm w przeglądarce lub silniku WASI, wzrostu pamięci JS oraz macierzy targetów: potrzebują docelowego hosta i adaptera; test std nie daje takiego dowodu.
- Kampanii fuzzingu, Miri, Loom i sanitizerów: potrzebują zależności lub osobnego toolchainu; szkice są oznaczone jako integracje i nie służą za deklarację wykonania.
- Wdrożeń, awarii baz, prawdziwej rotacji sekretów, alertów, exporterów i rollout: materiał dostarcza modele, procedury i kryteria projektów, a nie działające środowisko produkcyjne.
- Wykonania FFI na innych platformach oraz API od Rust 1.98 lokalnym 1.90: rozdzielono dostępność dokumentacji od dowodu wykonania. Wymagania NumBuffer potwierdzono dodatkowo w oficjalnej dokumentacji std.

Brak innych świadomie pominiętych zachowań istotnych dla przydzielonego zakresu przeglądu. Powyższe ograniczenia są zgodne z zadaniem kompendium i nie blokują akceptacji dokumentacyjnej.
