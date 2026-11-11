[← Spis treści](../README.md)
<!-- status: expanded -->

# Wydajność i zero-cost abstractions

## Cele

Po tym rozdziale potrafisz:

- zidentyfikować koszt alokacji, kopiowania i dostępu do pamięci w konkretnej ścieżce;
- wyrazić optymalizację jako mierzalną hipotezę z zachowaniem semantyki;
- porównać rozmiar kodu, przepustowość i opóźnienie przed przyjęciem zmiany;

## Model — mechanizm i kontrakt

„Zero-cost” znaczy: nie płacisz zasadniczo więcej niż za równoważną ręczną
implementację i nie płacisz za nieużywaną abstrakcję. Nie znaczy „każdy kod
jest darmowy”.

## Iteratory

~~~rust
fn suma_petla(dane: &[u64]) -> u64 {
    let mut wynik = 0;
    for &x in dane {
        wynik += x;
    }
    wynik
}

fn suma_iterator(dane: &[u64]) -> u64 {
    dane.iter().copied().sum()
}

fn main() {
    let dane = [1, 2, 3, 4];
    assert_eq!(suma_petla(&dane), suma_iterator(&dane));
}
~~~

Obie formy mogą wygenerować podobny kod. Potwierdza się to benchmarkiem i
profilem dla konkretnego targetu, nie samą stylistyką.

## Najczęstsze koszty

- alokacja i realokacja;
- kopiowanie dużych buforów;
- słaba lokalność cache i pointer chasing;
- dynamic dispatch i brak inliningu;
- synchronizacja oraz contention;
- syscall, sieć i dysk;
- nadmiarowa serializacja;
- rozmiar kodu po monomorfizacji.

`clone` nie zawsze jest drogi, a referencja nie zawsze szybsza. Klon `Arc`
jest inkrementacją atomową; klon `String` kopiuje bufor; klon małego `Copy`
to kilka bajtów.

## Layout i cache

`Vec<T>` przechowuje elementy ciągle, co sprzyja prefetch. Lista węzłów może
mieć teoretycznie tani insert, ale wiele alokacji i cache misses. Struct of
arrays bywa lepszy dla przetwarzania jednej kolumny; array of structs dla
przetwarzania pełnych rekordów. Pomiar rozstrzyga.

## Alokacje

Używaj `with_capacity`, jeśli rozmiar jest znany. Przyjmuj slices, aby nie
tworzyć kolekcji. Zwracaj iterator, gdy obliczenie może być leniwe. Nie
utrzymuj własnej puli obiektów bez profilu — może zwiększyć fragmentację i
złożoność.

## Profile kompilacji

`--release` zmienia optymalizację. LTO może poprawić inline między crate’ami
kosztem czasu linkowania. Mniej codegen units pomaga globalnej optymalizacji.
`target-cpu=native` może przyspieszyć lokalny program, lecz traci przenośność
binarną.

Profile-guided optimization i BOLT zależą od toolchainu/platformy i wymagają
reprezentatywnych profili. Sprawdzaj aktualny rustc Book.

## Bounds checks i `unsafe`

Optymalizator często usuwa bounds checks w prostych iteracjach. Nie przechodź
do `get_unchecked` bez dowodu z benchmarku i pełnego kontraktu bezpieczeństwa.
Jedna zła granica daje UB, a zysk może być zerowy.

## Metodyka

1. zdefiniuj metrykę i workload;
2. zmierz baseline w release;
3. użyj profilera;
4. postaw jedną hipotezę;
5. zmień jedną rzecz;
6. porównaj wynik i wariancję;
7. zachowaj regression benchmark.

Optymalizuj przepustowość, latency, pamięć, energię lub rozmiar świadomie —
cele mogą być sprzeczne.

## Analiza konkretnej zmiany

Załóżmy, że filtrujesz rekordy i budujesz tekstowy raport. Wersja `filter(...).map(...).collect::<Vec<_>>().join(...)` może materializować kolekcję pośrednią i wiele napisów. Wersja zapisująca bezpośrednio do jednego bufora zmniejsza liczbę obiektów, ale nie musi być szybsza, jeśli formatowanie lub I/O dominuje. Najpierw ustal udział tej ścieżki w całkowitym czasie, liczbę rekordów i wymóg atomowego wyniku.

~~~rust
use std::fmt::Write;
fn raport(dane: &[u32], bufor: &mut String) {
    bufor.clear();
    for &x in dane.iter().filter(|&&x| x > 10) {
        writeln!(bufor, "{x}").expect("zapis do String");
    }
}
fn main() {
    let mut bufor = String::with_capacity(64);
    raport(&[1, 11, 25], &mut bufor);
    assert_eq!(bufor, "11\n25\n");
    raport(&[7], &mut bufor);
    assert_eq!(bufor, "");
}
~~~

Ponowne użycie bufora zachowuje pojemność po `clear`, a więc amortyzuje alokacje kolejnych wywołań. Cena to retencja największej dotychczasowej pojemności. Jeden wyjątkowo duży raport może utrzymać pamięć długo po zakończeniu. Ustal pułap, po którym bufor jest odtwarzany albo zmniejszany. `with_capacity` przyjmuje wskazówkę początkową, nie ogranicza późniejszego wzrostu. Nie zakładaj konkretnego współczynnika powiększania `Vec`; kontrakt pojemności opisuje [dokumentacja Vec](https://doc.rust-lang.org/std/vec/struct.Vec.html), sprawdzona 2026-11-11.

Semantyka przykładu obejmuje końcowy newline; wersja z `join("\n")` może go nie dopisać. Optymalizacje porównuj dopiero po ustaleniu identycznego formatu. Dla bardzo dużego wyniku streaming do `Write` ograniczy pamięć, lecz może opublikować częściowy rezultat przed błędem. Szybkość, pamięć i atomowość to odrębne wymagania.

## Diagnostyka kompilatora

Próba zachowania slice do bufora i wywołania `clear` lub `push_str` przed ostatnim użyciem slice powoduje konflikt pożyczek. Nie „naprawiaj” go raw pointerem. Ogranicz życie widoku albo skopiuj tylko wynik potrzebny po zmianie. Taka diagnostyka często wskazuje, że planowana optymalizacja reuse wymaga zmiany kontraktu funkcji zwracającej pożyczone dane.

Z kolei panic przy sumowaniu dużych wartości w debug nie jest pomiarem wydajności. Określ semantykę przepełnienia: `checked_add`, `wrapping_add`, saturację albo dowiedzioną granicę. Porównanie debug i release bez tej decyzji może badać programy o innym zachowaniu. Test poprawności musi obejmować przypadki graniczne niezależnie od benchmarku.

## Praktyka produkcyjna

Zysk lokalny ogranicza udział optymalizowanego fragmentu. Jeśli parser zajmuje 10% czasu żądania, nawet jego dwukrotne przyspieszenie daje około 5% poprawy całej ścieżki przy pozostałych kosztach bez zmian. Optymalizacja alokacji może jednak zmniejszyć ogon opóźnień i szczyt pamięci, czego średni czas nie pokaże. Zapisuj kilka metryk i wybierz warunki akceptacji przed pomiarem.

Profile Cargo mają osobne ustawienia optymalizacji, symboli i kontroli przepełnienia. `lto` oraz `codegen-units` wpływają na optymalizację i czas budowania; mniej jednostek nie jest obietnicą przyspieszenia aplikacji. Wyższy poziom optymalizacji ani `"z"` nie gwarantują lepszego wyniku dla każdego programu. Status ustawień sprawdzono w [Cargo profiles](https://doc.rust-lang.org/cargo/reference/profiles.html), 2026-11-11. Zapisz manifest, flagi CPU i target razem z wynikami, aby porównanie było odtwarzalne.

PGO wymaga zbudowania instrumentowanej wersji, zebrania reprezentatywnego ruchu, połączenia profili i ponownego budowania z ich użyciem. Profil pochodzący z jednego nietypowego klienta może pogorszyć inne scenariusze. Sprawdź [procedurę rustc PGO](https://doc.rust-lang.org/rustc/profile-guided-optimization.html), zweryfikowaną 2026-11-11; tutaj nie wykonywano profilowania PGO ani postlinkowej optymalizacji BOLT.

## Sprawdź, czy rozumiesz

- Kiedy bufor reuse zmniejszy alokacje, lecz zwiększy stałą pamięć procesu?
- Dlaczego usunięcie bounds check nie musi zmienić czasu aplikacji?
- Jak wykryjesz, że szybszy raport zmienił końcowy newline?

## Ćwiczenia

- `C10-1` — podstawowe: Oblicz maksymalny zysk całkowity po dwukrotnym przyspieszeniu fragmentu zajmującego 40% czasu. Przyjmij brak innych zmian. [Rozwiązanie](../rozwiazania/20_wydajnosc_i_optymalizacja/01_wydajnosc_i_zero_cost.md#c10-1).
- `C10-2` — praktyczne: Zaprojektuj wariant raportu z limitem retencji bufora 1 MiB. Określ moment zwolnienia pamięci i test zachowania tekstu. [Rozwiązanie](../rozwiazania/20_wydajnosc_i_optymalizacja/01_wydajnosc_i_zero_cost.md#c10-2).
- `C10-3` — pogłębione: Porównaj listę węzłów, Vec<Rekord> i strukturę kolumnową dla sumowania jednej kolumny miliona rekordów. Zapisz hipotezy oraz miary, bez wymyślania wyników. [Rozwiązanie](../rozwiazania/20_wydajnosc_i_optymalizacja/01_wydajnosc_i_zero_cost.md#c10-3).

## Powiązane tematy

- [Benchmarki i profilowanie](../20_wydajnosc_i_optymalizacja/02_benchmarki_profilowanie_i_miri.md)
- [Monomorfizacja, MIR i LLVM](../20_wydajnosc_i_optymalizacja/03_monomorfizacja_mir_llvm_i_optymalizacja.md)
- [Layout i alignment](../21_unsafe_soundness_i_model_pamieci/03_layout_alignment_i_uninitialized_memory.md)
