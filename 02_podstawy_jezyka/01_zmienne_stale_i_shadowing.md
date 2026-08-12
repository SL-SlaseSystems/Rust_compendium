[← Spis treści](../README.md)

# Zmienne, stałe i shadowing

Zmienne są domyślnie niemutowalne. To sygnał projektowy: po inicjalizacji
wartość nie zmieni się przypadkiem.

~~~rust
fn main() {
    let port = 8080;
    assert_eq!(port, 8080);

    let mut licznik = 0;
    licznik += 1;
    assert_eq!(licznik, 1);
}
~~~

`mut` pozwala zmienić wartość, ale nie jej typ. Kompilator wymaga też
inicjalizacji przed odczytem:

~~~rust
fn main() {
    let wynik: i32;
    if true {
        wynik = 42;
    } else {
        wynik = 0;
    }
    assert_eq!(wynik, 42);
}
~~~

## Shadowing

Ponowne `let` tworzy nową zmienną o tej samej nazwie. Może zmienić typ:

~~~rust
fn main() {
    let wejscie = " 41 ";
    let wejscie = wejscie.trim();
    let wejscie: i32 = wejscie.parse().expect("liczba");
    let wejscie = wejscie + 1;
    assert_eq!(wejscie, 42);
}
~~~

Shadowing jest dobry dla kolejnych etapów przekształcania tej samej wartości.
`mut` jest lepsze, gdy tożsamość obiektu pozostaje ta sama, a zmienia się jego
stan.

## Stałe i wartości statyczne

`const` wymaga typu i wyrażenia możliwego do policzenia podczas kompilacji:

~~~rust
const SEKUNDY_NA_GODZINE: u32 = 60 * 60;

fn main() {
    assert_eq!(SEKUNDY_NA_GODZINE, 3600);
}
~~~

`static` oznacza pojedyncze miejsce w pamięci o czasie życia całego programu.
Mutowalne `static mut` jest `unsafe` i prawie zawsze lepiej zastąpić je
bezpieczną synchronizacją, np. `AtomicUsize` albo `Mutex`.

## Zakres i destrukcja

Nazwa jest widoczna od deklaracji do końca bloku. Wartość posiadająca zasób
jest niszczona przy wyjściu z zakresu, w kolejności odwrotnej do utworzenia.

~~~rust
fn main() {
    let x = 1;
    {
        let x = x + 1;
        assert_eq!(x, 2);
    }
    assert_eq!(x, 1);
}
~~~

## Pułapki

- nie używaj shadowing do ukrywania zupełnie innego pojęcia;
- `const` nie jest tylko „niemutowalnym `let`” — nie ma adresu jednej
  globalnej instancji;
- niemutowalność bindingu nie zawsze oznacza głęboką niemutowalność; typy
  takie jak `Cell` mogą realizować interior mutability.

## Powiązane tematy

- [Typy i konwersje](02_typy_i_konwersje.md)
- [Stos, sterta i RAII](../03_pamiec_i_wlasnosc/01_stos_sterta_i_raii.md)
- [Smart pointery i interior mutability](../03_pamiec_i_wlasnosc/06_smart_pointery_i_interior_mutability.md)
