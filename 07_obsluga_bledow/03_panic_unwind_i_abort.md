[← Spis treści](../README.md)
<!-- status: expanded -->

# `panic!`, unwind i abort

## Cele

Po tym rozdziale potrafisz:

- odróżnić odzyskiwanie z błędu od rozwijania stosu;
- zachować niezmiennik przy panic i opisać ograniczenia przechwytywania;


Panic sygnalizuje sytuację, której bieżący kod nie potrafi lub nie powinien
obsługiwać jako zwykłego wyniku: złamany invariant, błąd programisty albo
nieobsługiwalny stan procesu. Nie jest zamiennikiem `Result` dla błędnych
danych użytkownika.

## Źródła panic

Jawne `panic!`, `assert!`, `unwrap`, indeks poza zakresem i część operacji
arytmetycznych może uruchomić panic.

~~~rust
fn pierwiastek(x: f64) -> f64 {
    assert!(x >= 0.0, "pierwiastek wymaga x >= 0, otrzymano {x}");
    x.sqrt()
}

fn main() {
    assert_eq!(pierwiastek(9.0), 3.0);
}
~~~

Biblioteka powinna dokumentować sekcję `# Panics` dla warunków wynikających z
publicznego wejścia. Lepiej jednak użyć typu lub `Result`, jeśli naruszenie
jest spodziewane.

## Unwind i abort

Przy strategii `unwind` stos jest rozwijany, a destruktory lokalnych wartości
są uruchamiane. Przy `abort` proces kończy się bez unwinding. Strategię można
ustawić w profilu:

To fragment manifestu lub konfiguracji; wymaga właściwego projektu i nie jest samodzielnym doctestem.

~~~text
[profile.release]
panic = "abort"
~~~

Nie zakładaj w logice biznesowej, że destruktor zawsze wykona efekt zewnętrzny.
Nagłe przerwanie procesu, błąd systemu lub abort mogą temu zapobiec.

## `catch_unwind`

Standard library pozwala przechwycić część panic z unwinding:

~~~rust
use std::panic;

fn main() {
    let wynik = panic::catch_unwind(|| {
        panic!("kontrolowany panic");
    });
    assert!(wynik.is_err());
}
~~~

To nie jest ogólny mechanizm wyjątków. Nie przechwytuje abort, panic może użyć
niestandardowego hooka, a granica wymaga `UnwindSafe`. `catch_unwind` jest
przydatne głównie na granicach runtime’u, pluginu lub FFI, gdzie trzeba
powstrzymać unwinding przed przekroczeniem kontraktu.

## Panic safety

Kod mutujący strukturę powinien zachować co najmniej:

- **basic guarantee** — po panic obiekt pozostaje bezpieczny do zniszczenia;
- **strong guarantee** — operacja albo kończy się w całości, albo nie zmienia
  stanu.

Bezpieczny Rust chroni memory safety, ale nie automatycznie invariant logiczny.
Guardy RAII i kolejność operacji „najpierw przygotuj, potem zatwierdź” pomagają
zachować spójność.

## Hook i backtrace

`std::panic::set_hook` może zmienić raport. Zmienna `RUST_BACKTRACE=1` pomaga
w diagnostyce, jeśli binarium ma potrzebne informacje. Nie pokazuj
użytkownikowi sekretów z komunikatów i backtrace.


## Model — sprzątanie nie jest wycofaniem

Panic przerywa normalny przepływ. W strategii unwind uruchamia destruktory podczas opuszczania kolejnych ramek stosu; nie przywraca poprzednich wartości pól. Jeżeli kod najpierw usunął element z kolekcji, a dopiero potem wywołał panikujący callback, sam fakt istnienia destruktorów nie odtworzy elementu. Bezpieczeństwo pamięci i spójność domenowa to różne zobowiązania.

Praktyczny wzorzec przygotowuje nowy stan obok starego, a następnie zatwierdza krótką operacją. Gdy przygotowanie zawiedzie, stary stan pozostaje dostępny. To działa tylko w granicach założeń: klonowanie danych może być kosztowne, `Drop` może wykonywać własny kod, a transakcja zewnętrzna wymaga gwarancji zasobu. Warto nazwać gwarancję w dokumentacji zamiast obiecywać ogólne „bezpieczne po błędzie”.

~~~rust
fn zastap(aktualne: &mut Vec<u32>, wejscie: &[&str]) -> Result<(), std::num::ParseIntError> {
    let nowe: Result<Vec<u32>, _> = wejscie.iter().map(|s| s.parse()).collect();
    *aktualne = nowe?;
    Ok(())
}
fn main() {
    let mut dane = vec![7];
    assert!(zastap(&mut dane, &["1", "x"]).is_err());
    assert_eq!(dane, [7]);
    zastap(&mut dane, &["1", "2"]).unwrap();
    assert_eq!(dane, [1, 2]);
}
~~~

Przykład używa `Result`, bo zły tekst jest spodziewany. Ta sama kolejność „przygotuj, zatwierdź” ogranicza skutki panic w bardziej złożonych konstruktorach. Dopiero po pełnym parsowaniu następuje przypisanie. Zapłatą jest przejściowe utrzymywanie dwóch wektorów.

`UnwindSafe` opisuje ryzyko obserwowania stanu po przechwyconym unwind. Nie jest dowodem bezpieczeństwa całej aplikacji. `AssertUnwindSafe` wyłącza ostrzeżenie typowe i przenosi odpowiedzialność na autora; nie naprawia częściowo zmienionych pól. Stosuj go do wąskiej, przeanalizowanej granicy zamiast obejmować nim cały subsystem.

Hook panic działa również wtedy, gdy unwind zostanie przechwycony. Dlatego oczekiwany panic w teście może nadal wypisać komunikat. Hook jest globalnym zasobem procesu; jego wymiana podczas równoległych testów powoduje interferencję. Destruktor panikujący w trakcie istniejącego unwind może zakończyć proces, więc cleanup powinien mieć bardzo ograniczoną możliwość błędu.

Na granicach FFI znaczenie ma ABI. Nie wolno obiecywać, że `catch_unwind` przechwyci dowolny wyjątek obcego języka ani panic realizowany abort. Dla `extern "C"` panic przekraczający niedozwoloną granicę prowadzi do zakończenia procesu. Tam, gdzie API wymaga kodu błędu, tłumaczenie wyniku należy zaprojektować przed opuszczeniem granicy Rusta.

## Diagnostyka kompilatora

Przekazanie closure przechwytującego `&mut Vec<_>` do `catch_unwind` może zostać odrzucone z powodu `UnwindSafe`. Najpierw sprawdź, co po panic zobaczy wywołujący. Jeżeli spodziewany błąd pochodzi z wejścia, poprawnym rozwiązaniem zwykle jest `Result`. Samodzielny `panic!(123)` nie jest poprawną współczesną składnią komunikatu; użyj formatowania lub `panic_any` dla świadomego payloadu. Nie uzależniaj programu od dokładnego tekstu standardowej diagnostyki panic.

## Praktyka produkcyjna

Wybór abort może zmniejszyć koszty obsługi unwind, lecz zmienia zachowanie sprzątania i granic odzyskiwania. Testuj proces potomny, gdy sprawdzasz zakończenie procesu; zwykły test we wspólnym procesie nie może bezpiecznie przeżyć abort. Dokumentuj `# Panics` dla publicznego API i unikaj sekretów w payloadzie. Po przechwyceniu panic nie kontynuuj obsługi żądania bez sprawdzenia spójności. Często lepsza jest izolacja workera lub restart procesu niż próba ratowania nieznanego stanu.

## Sprawdź, czy rozumiesz

- Dlaczego działający `Drop` nie oznacza rollbacku?
- Co pozostaje nieudowodnione po użyciu `AssertUnwindSafe`?
- Jak testować `panic = "abort"` bez zatrzymania całego harnessu?

## Ćwiczenia

- `B03-1` — podstawowe: Przechwyć panic przy unwind i sprawdź `is_err`. [Rozwiązanie](../rozwiazania/07_obsluga_bledow/03_panic_unwind_i_abort.md#b03-1).
- `B03-2` — praktyczne: Napisz walidowaną zamianę wektora, która zachowuje stary stan przy błędzie. [Rozwiązanie](../rozwiazania/07_obsluga_bledow/03_panic_unwind_i_abort.md#b03-2).
- `B03-3` — pogłębione: Zademonstruj przez guard i licznik, że lokalny destruktor działa podczas przechwyconego unwind. [Rozwiązanie](../rozwiazania/07_obsluga_bledow/03_panic_unwind_i_abort.md#b03-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [catch_unwind i ograniczenia](https://doc.rust-lang.org/std/panic/fn.catch_unwind.html)
- [UnwindSafe](https://doc.rust-lang.org/std/panic/trait.UnwindSafe.html)

## Powiązane tematy

- [Własne błędy i API](04_wlasne_bledy_i_api.md)
- [RAII](../03_ownership_i_pamiec/01_stos_sterta_i_raii.md)
- [FFI, bezpieczne otoczki i UB](../22_ffi_i_interoperacyjnosc/02_ffi_safe_wrappers_i_ub.md)
