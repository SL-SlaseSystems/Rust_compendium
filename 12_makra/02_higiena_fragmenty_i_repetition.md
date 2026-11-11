[← Spis treści](../README.md)
<!-- status: expanded -->

# Higiena, fragmenty i repetition

## Cele

Po tym rozdziale potrafisz:

- dobrać fragment i separator bez lokalnej dwuznaczności;
- wyjaśnić częściową higienę i wpływ edition definicji;


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


## Model — fragment jest obietnicą parsera

Wybór `expr` mówi parserowi, że wejście ma być kompletnym wyrażeniem. Po przekazaniu do kolejnego makra jest ono traktowane jako nieprzezroczysty fragment tego rodzaju. Jeżeli chcesz rozpoznawać konkretne pojedyncze tokeny na dalszym etapie, użyj właściwego `tt` albo projektuj jawny znacznik. Nadmierne użycie `tt` usuwa jednak pomoc parsera i przenosi pracę do twojej gramatyki.

Powtórzenia wymagają zgodności struktury. Metazmienna przechwycona wewnątrz zagnieżdżonego powtórzenia musi być rozwijana z odpowiednią głębokością. Dwie listy użyte w jednym powtórzeniu muszą mieć zgodne liczności; nie jest to automatyczny iloczyn kartezjański. Zamiast walczyć ze złożonym zagnieżdżeniem, rozważ uproszczenie składni wejścia do list par.

~~~rust
macro_rules! pary {
    ($($nazwa:ident => $wartosc:expr),* $(,)?) => {
        $(let $nazwa = $wartosc;)*
    };
}
fn main() {
    pary!(a => 2, b => 5,);
    assert_eq!(a + b, 7);
}
~~~

Bindingi w tym przykładzie celowo pochodzą z identyfikatorów przekazanych przez użytkownika. Dzięki temu są dostępne po wywołaniu makra. To inny przypadek niż pomocnicze `let wynik` zapisane wyłącznie w definicji, które ma własny kontekst składniowy. Nie uznawaj higieny za zakaz generowania nazw użytkownika ani za pełną ochronę każdego itemu.

`$crate` wskazuje crate definicji, również po zmianie nazwy zależności. Nie omija jednak prywatności. Jeżeli eksportowane makro ma wywołać helper z innego crate’a, helper musi być osiągalny zgodnie z regułami widoczności. `#[doc(hidden)]` ukrywa go w zwykłej dokumentacji, ale nie usuwa technicznej publiczności ani odpowiedzialności za jego stabilność.

Edition 2024 rozszerza `expr` o wyrażenia `const` i `_`. Kluczowa jest edition definicji makra. Może to zmienić, które ramię zostanie wybrane, jeżeli wcześniej specjalne ramię zaczynało się od `const`. `expr_2021` zachowuje wcześniejsze dopasowanie. Migracja nie powinna polegać wyłącznie na automatycznej zmianie nazwy fragmentu; sprawdź zamierzony zakres składni i kolejność ramion.

Follow-set ogranicza dozwolone tokeny po fragmentach, aby przyszłe rozszerzenia języka nie zmieniały arbitralnie interpretacji. Separatory takie jak przecinek i średnik pomagają oddzielać elementy DSL. Długi TT muncher może mieć kwadratowy koszt przetwarzania, ponieważ kolejne kroki ponownie dopasowują pozostały ogon. Podniesienie `recursion_limit` usuwa objaw limitu, ale nie zmniejsza kosztu algorytmu ekspansji.

## Diagnostyka kompilatora

Komunikat o „attempted to repeat an expression containing no syntax variables matched as repeating” oznacza złą strukturę repetition, a nie błąd typów. `local ambiguity` wskazuje niedookreśloną gramatykę przy bieżącym tokenie. Błąd prywatnego helpera po ekspansji wymaga zaprojektowania publicznej ścieżki makra. Nie poprawiaj go za pomocą niekwalifikowanej nazwy, która zadziała tylko przy przypadkowym imporcie u autora.

## Praktyka produkcyjna

Dla stabilnego DSL utrzymuj testy pustych list, list pojedynczych i zagnieżdżonych oraz niepoprawnych separatorów. Testuj definicję i konsumenta z odpowiednimi editions. Makra eksportowane sprawdzaj poza własnym crate’em, z aliasem zależności i lokalnymi nazwami mogącymi kolidować z helperami. Profiluj czas kompilacji przy realistycznie dużym wejściu. Czasem prostszy format danych lub funkcja eliminuje cały problem ekspansji i daje lepszy kontrakt błędu.

## Sprawdź, czy rozumiesz

- Dlaczego `$crate` nie omija prywatności?
- Która edition decyduje o dopasowaniu `expr`?
- Czy dwie listy w repetition automatycznie tworzą wszystkie pary?

## Ćwiczenia

- `B25-1` — podstawowe: Napisz makro listy par identyfikator–wartość z końcowym przecinkiem. [Rozwiązanie](../rozwiazania/12_makra/02_higiena_fragmenty_i_repetition.md#b25-1).
- `B25-2` — praktyczne: Pokaż higienę pomocniczego bindingu o nazwie takiej jak u wywołującego. [Rozwiązanie](../rozwiazania/12_makra/02_higiena_fragmenty_i_repetition.md#b25-2).
- `B25-3` — pogłębione: Porównaj wybór ramienia `expr` i `const expr` po migracji do Edition 2024. [Rozwiązanie](../rozwiazania/12_makra/02_higiena_fragmenty_i_repetition.md#b25-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Reference: fragmenty i higiena](https://doc.rust-lang.org/reference/macros-by-example.html)
- [Edition 2024: expr i expr_2021](https://doc.rust-lang.org/edition-guide/rust-2024/macro-fragment-specifiers.html)

## Powiązane tematy

- [`macro_rules!`](01_macro_rules.md)
- [Makra proceduralne](03_makra_proceduralne.md)
- [Edition i feature gates](../08_moduly_cargo_i_workspaces/05_nightly_unstable_i_feature_gates.md)
