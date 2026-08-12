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
