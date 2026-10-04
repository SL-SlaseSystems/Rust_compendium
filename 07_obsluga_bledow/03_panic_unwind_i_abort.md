[← Spis treści](../README.md)

# `panic!`, unwind i abort

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

~~~toml
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

## Powiązane tematy

- [Własne błędy i API](04_wlasne_bledy_i_api.md)
- [RAII](../03_ownership_i_pamiec/01_stos_sterta_i_raii.md)
- [FFI, bezpieczne otoczki i UB](../zaawansowane/11_ffi_safe_wrappers_i_ub.md)
