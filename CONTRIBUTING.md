# Zasady rozwijania kompendium

[← Spis treści](README.md)

## Styl

Pisz po polsku, zdaniami możliwie krótkimi, ale zachowuj angielski termin
przy pierwszym użyciu: „własność (ownership)”, „pożyczanie (borrowing)”.
Nazwy elementów języka i API zapisuj jako kod. Nie nazywaj crate’a
„biblioteką standardową”, jeśli pochodzi z crates.io.

## Minimalna budowa rozdziału

1. Cel i intuicja.
2. Reguły lub model mentalny.
3. Przykład.
4. Omówienie przykładu.
5. Typowe błędy i pułapki.
6. Dobre praktyki.
7. Powiązane tematy.

Układ wolno skrócić, gdy dana sekcja nie wnosi informacji.

## Rozdział rozszerzony

Rozdział rozszerzony zaczyna się dokładnie od poniższego nagłówka:

~~~markdown
[← Spis treści](../README.md)
<!-- status: expanded -->

# Tytuł

## Cele

Po tym rozdziale potrafisz:

- opisać konkretny rezultat;
- zastosować konkretną regułę.
~~~

Musi zawierać: `## Cele`, model lub reguły, poprawny blok `rust`,
`## Diagnostyka kompilatora`, `## Praktyka produkcyjna`,
`## Sprawdź, czy rozumiesz`, `## Ćwiczenia` oraz `## Powiązane tematy`.
Cele opisują sprawdzalne rezultaty, a nie tylko zakres omawianego materiału.

## Ćwiczenia

Każde ćwiczenie ma identyfikator w postaci `<dział><rozdział>-<numer>`,
na przykład `O02-1`. Wpis podaje jeden poziom: „podstawowe”, „praktyczne”
albo „pogłębione”, oraz link do dokładnej kotwicy w `rozwiazania/`.

Przykład:

~~~markdown
- `O02-1` — podstawowe: rozwiąż zadanie i porównaj z [rozwiązaniem](../rozwiazania/ownership.md#o02-1).
~~~

## Bloki kodu

Samowystarczalny kod oznaczaj jako Rust:

~~~rust
fn main() {
    println!("przykład samowystarczalny");
}
~~~

Kod, który ma zostać odrzucony przez kompilator, oznaczaj tak:

~~~compile_fail
fn main() {
    let x = String::from("przeniesiono");
    let y = x;
    println!("{x} {y}");
}
~~~

Manifesty, szkice API z crate’ów zewnętrznych i pseudokod oznaczaj jako
`text`. Komentarz przed blokiem ma powiedzieć, dlaczego nie jest on testowany.

## Stabilność

- **stable** — działa na wskazanej minimalnej wersji stabilnej;
- **nightly** — wymaga kanału nightly oraz podanej bramki `#![feature(...)]`;
- **third-party** — wymaga crate’a spoza dystrybucji Rusta.

Przy treściach zmiennych podawaj datę weryfikacji. Nie przedstawiaj planowanej
funkcjonalności jako gwarantowanej części przyszłego wydania.

## Aktualność źródeł

Przy rozbieżności pierwszeństwo mają Rust Reference i aktualna dokumentacja
API, a dopiero potem Rustonomicon. Każdą informację zależną od kanału lub
zewnętrznej zależności oznacz osobno jako **stable**, **nightly** albo
**third-party**. Przy twierdzeniu zależnym od wydania podaj datę weryfikacji.
Nie pisz „sprawdzone na Rust 1.98.1”, jeśli przykład nie został wykonany tym
toolchainem.

## Linki i odsyłacze

Każdy rozdział zaczyna się dokładnie od:

~~~text
[← Spis treści](../README.md)
~~~

Kończy się sekcją `## Powiązane tematy` z dwoma do pięciu linków. Linkuj do
plików względnie, bez ścieżek systemowych.

## Kontrola

Przed uznaniem zmian za gotowe uruchom `bash scripts/verify.sh`. Celowo błędny
przykład musi być blokiem `compile_fail` i zawierać wyjaśnienie rodzaju błędu.

## Powiązane tematy

- [Spis treści](README.md)
- [Źródła](zrodla.md)
