[← Spis treści](../../README.md)

# Rozwiązania: Unsafe i soundness

## C13-1

Zmiana jest niepoprawna. Dla slice o długości 2 i `srodek=3` kontrola znika w release, a implementacja może wykonać niedozwoloną arytmetykę i skonstruować niepoprawne widoki. Nie trzeba uruchamiać tego przypadku: bezpieczna sygnatura akceptuje każdy `usize`, więc musi sama odrzucić złą granicę albo zwrócić błąd. `assert!` pozostaje aktywne we wszystkich profilach. Alternatywa to `Option` lub `Result`, również ze sprawdzeniem w release.

## C13-2

~~~rust
fn kopiuj<T: Copy>(wartosc: &T) -> T { *wartosc }
fn main() {
    let x = 42;
    assert_eq!(kopiuj(&x), 42);
}
~~~

Referencja niesie wymagania ważności wartości i dostępu, które bezpieczny kod utrzymuje dzięki typom. Implementacja nie potrzebuje unsafe. Wersja raw przydaje się tylko wtedy, gdy rzeczywiście trzeba obsłużyć granicę bez referencji; wtedy wywołujący musi udowodnić alignment, inicjalizację, ważność dostępu i pozostałe wymagania pointer API.

## C13-3

Dla `size_of::<T>() > 0` pole `ptr` wskazuje alokację o pojemności `cap`, poprawnym alignment i właściwej parze alloc/dealloc; `0 <= len <= cap`, a dokładnie prefix `0..len` zawiera żywe wartości. ZST wymaga osobnego protokołu bez założenia realnej alokacji i z poprawną liczbą logicznych dropów. Konstruktor pusty zapewnia legalny sentinel i zerową długość. `push` najpierw zapewnia pojemność, potem zapisuje nową wartość, dopiero potem zwiększa `len`. `pop` zmniejsza `len` przed oddaniem przenoszonego elementu.

`Drop` niszczy tylko żywy prefix i zwalnia alokację właściwym layoutem. Błąd alokacji lub panic przed zakończeniem zapisu nie może zwiększyć długości. Przy realokacji stary bufor przestaje być własnością kolekcji dopiero po poprawnym przeniesieniu odpowiedzialności. Audyt obejmuje przepełnienie `cap * size_of::<T>()`, ZST, panic destructora oraz bezpieczne metody zmieniające pola. W praktyce użyj `Vec<T>`; to lista obowiązków, nie kompletna implementacja własnego wektora.
