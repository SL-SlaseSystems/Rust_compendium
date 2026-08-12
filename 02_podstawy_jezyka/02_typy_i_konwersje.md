[← Spis treści](../README.md)

# Typy i konwersje

Rust jest statycznie typowany, ale często wnioskuje typ z kontekstu. Jawna
adnotacja jest potrzebna, gdy istnieje kilka możliwości albo poprawia
czytelność.

## Typy skalarne

- liczby całkowite: `i8`…`i128`, `u8`…`u128`, `isize`, `usize`;
- zmiennoprzecinkowe: `f32`, `f64`;
- `bool`;
- `char` — pojedyncza wartość skalara Unicode, cztery bajty.

~~~rust
fn main() {
    let calkowita: u32 = 1_000;
    let szesnastkowa = 0xff_u8;
    let zmienna = 2.5_f64;
    let znak = '🦀';
    assert_eq!((calkowita, szesnastkowa, zmienna, znak), (1000, 255, 2.5, '🦀'));
}
~~~

`usize` jest typem indeksów i rozmiarów kolekcji. Jego szerokość zależy od
platformy. Nie używaj `f32`/`f64` do dokładnych kwot pieniężnych.

## Typy złożone

Krotka ma pola różnych typów, a tablica — stałą długość i jeden typ elementu:

~~~rust
fn main() {
    let punkt: (i32, i32) = (3, 4);
    let [pierwsza, .., ostatnia] = [10, 20, 30, 40];
    assert_eq!(punkt.0, 3);
    assert_eq!((pierwsza, ostatnia), (10, 40));
}
~~~

`()` to typ jednostkowy (unit). Typ `!` oznacza, że obliczenie nigdy normalnie
nie zwraca, np. nieskończona pętla lub funkcja kończąca proces.

## Arytmetyka

Przepełnienie integera w debug zwykle powoduje panic, a w release może
zawijać zgodnie z arytmetyką uzupełnienia do dwóch. Intencję zapisuj jawnie:

~~~rust
fn main() {
    assert_eq!(255_u8.checked_add(1), None);
    assert_eq!(255_u8.wrapping_add(1), 0);
    assert_eq!(250_u8.saturating_add(20), 255);
    assert_eq!(2_u32.pow(10), 1024);
}
~~~

## Konwersje

Rust nie wykonuje ogólnych niejawnych konwersji liczbowych. `as` wykonuje
rzutowanie według ściśle zdefiniowanych reguł, ale może obciąć wartość.
Do konwersji sprawdzanej używaj `TryFrom`:

~~~rust
use std::convert::TryFrom;

fn main() {
    let duza = 300_u16;
    assert!(u8::try_from(duza).is_err());

    let mala = 42_u16;
    let wynik = u8::try_from(mala).unwrap();
    assert_eq!(wynik, 42);
}
~~~

`From`/`Into` opisują konwersję nieomylną, `TryFrom`/`TryInto` — omylną.
`parse::<T>()` konwertuje tekst, jeśli typ implementuje `FromStr`.

Alias `type Id = u64;` daje drugą nazwę, ale nie tworzy nowego typu. Jeśli
kompilator ma rozróżniać semantycznie identyczne reprezentacje, użyj wzorca
newtype.

## Powiązane tematy

- [Konwersje, DST i trait objects](../04_typy_i_modelowanie/05_konwersje_dst_i_trait_objects.md)
- [`Option` i `Result`](../06_bledy/01_option_i_result.md)
- [Idiomy i newtype](../13_wzorce_i_architektura/01_idiomy_newtype_i_extension_traits.md)
