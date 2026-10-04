[← Spis treści](../README.md)

# Higiena, fragmenty i repetition

## Fragment specifiers

Najważniejsze fragmenty matchera:

- `expr` — wyrażenie;
- `ty` — typ;
- `pat` / `pat_param` — wzorzec;
- `path` — ścieżka;
- `ident` — pojedynczy identyfikator lub keyword dopuszczony regułą;
- `item`, `stmt`, `block`, `meta`, `vis`, `literal`;
- `tt` — pojedyncze token tree;
- `lifetime`.

Przekazany fragment staje się dla kolejnego makra nieprzezroczystym AST.
Wyjątki takie jak `ident`, `lifetime` i `tt` mogą być ponownie dopasowywane
literalnymi tokenami.

~~~rust
macro_rules! utworz_funkcje {
    ($nazwa:ident, $typ:ty, $wartosc:expr) => {
        fn $nazwa() -> $typ {
            $wartosc
        }
    };
}

utworz_funkcje!(odpowiedz, u32, 40 + 2);

fn main() {
    assert_eq!(odpowiedz(), 42);
}
~~~

## Repetition

`*` oznacza zero lub więcej, `+` co najmniej jedno, `?` najwyżej jedno.
Metazmienne w transcriberze muszą zachować zgodną głębokość i liczbę
powtórzeń.

~~~rust
macro_rules! mapa {
    ($($klucz:expr => $wartosc:expr),* $(,)?) => {{
        let mut m = std::collections::BTreeMap::new();
        $(m.insert($klucz, $wartosc);)*
        m
    }};
}

fn main() {
    let m = mapa!("b" => 2, "a" => 1,);
    assert_eq!(m.keys().copied().collect::<Vec<_>>(), ["a", "b"]);
}
~~~

## Higiena

Nazwy wprowadzone wewnątrz makra nie powinny przypadkiem przechwytywać
lokalnych bindingów wywołującego. Rust ma częściową higienę: lifetimes,
labels i lokalne zmienne są rozróżniane składniowo, ale ścieżki i items
wymagają świadomego kwalifikowania.

`$crate` odwołuje się do crate’a, w którym zdefiniowano makro, nawet gdy
konsument zmienił jego nazwę:

~~~rust
pub fn jeden() -> u8 { 1 }

macro_rules! lokalny_jeden {
    () => { $crate::jeden() };
}

fn main() {
    assert_eq!(lokalny_jeden!(), 1);
}
~~~

## Rekurencja i munchery

Makro może wywołać samo siebie i przetwarzać listę token po tokenie
(TT muncher). Jest to kosztowne kwadratowo dla długich wejść i ograniczone
`recursion_limit`. Preferuj zwykłe repetition; parser proceduralny jest
lepszy dla złożonej gramatyki.

## Follow-set i editions

Po niektórych fragmentach mogą występować tylko określone tokeny, aby przyszła
składnia języka nie stała się dwuznaczna. Zachowanie `expr` i `pat` może zależeć
od edition crate’a definiującego makro. Migracje edition mają dedykowane
fragmenty zgodności, np. `expr_2021`; sprawdzaj Edition Guide.

## Diagnostyka

Dodaj ramię `compile_error!` dla rozpoznawalnych, błędnych form. Utrzymuj
małe matchery i testy `compile_fail` dla komunikatów. `cargo expand` jest
narzędziem **third-party** pokazującym rozwinięcie.

## Powiązane tematy

- [`macro_rules!`](01_macro_rules.md)
- [Makra proceduralne](03_makra_proceduralne.md)
- [Edition i feature gates](../08_moduly_cargo_i_workspaces/05_nightly_unstable_i_feature_gates.md)
