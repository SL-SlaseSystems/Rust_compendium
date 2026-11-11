[← Spis treści](../../README.md)

# Rozwiązania: Raw pointers i provenance

## C14-1

Warunek `len >= 3`, pochodzenie z żywego slice, alignment `u32`, inicjalizacja trzeciego elementu, brak kolidującej mutacji i odczyt wewnątrz zakresu stanowią przesłanki. `u32: Copy` oznacza, że zwracany wynik nie tworzy drugiego właściciela zasobu. Bezpieczny odpowiednik: `fn trzeci(dane: &[u32]) -> Option<u32> { dane.get(2).copied() }`. Obejmuje także puste i krótsze wejścia bez panic.

## C14-2

~~~rust
fn drugie(dane: &[u8]) -> Option<u32> {
    let bajty: [u8; 4] = dane.get(4..8)?.try_into().ok()?;
    Some(u32::from_le_bytes(bajty))
}
fn main() {
    assert_eq!(drugie(&[0, 0, 0, 0, 1, 2, 0, 0]), Some(513));
    assert_eq!(drugie(&[0; 7]), None);
    assert_eq!(drugie(&[]), None);
}
~~~

Kopiowanie czterech bajtów do tablicy nie wymaga wyrównania wejścia dla `u32`. Endianness jest jawnie cechą protokołu, a nie targetu. Nie ma referencji do `u32` w buforze ani ryzyka naruszenia provenance.

## C14-3

Konstrukcja jest niedozwolona przez kontrakt `from_raw_parts`: cały niepusty zakres musi należeć do jednej alokacji. Sąsiednie adresy nie łączą historii alokacji ani właścicieli. Bez kopiowania zwróć strukturę zawierającą dwa slices albo iterator łączący oba zakresy. Jeśli odbiorca wymaga jednego ciągłego slice, skopiuj oba do jednego `Vec`, z kontrolą łącznej długości i błędu rezerwacji według wymagań produktu. `repr(C)` wrappera ani cast przez integer nie naprawiają sytuacji.
