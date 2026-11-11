[← Spis treści](../../README.md)

# Rozwiązania: Monomorfizacja i optymalizacja

## C12-1

Wywołania wymagają `policz::<&str>` oraz `policz::<String>`. Oba przekazują widok do `rdzen(&str)`. Kompilator może usuwać martwy kod, inlinować wrappery i przekształcać wywołania; linker może scalać identyczne fragmenty. Liczba funkcji źródłowych i potrzebnych instancji jest modelem kosztu codegen, a nie stabilnym kontraktem tabeli symboli.

## C12-2

~~~rust
fn poprawny_naglowek(dane: &[u8]) -> bool {
    dane.starts_with(b"RUST") && dane.len() <= 1024
}
fn sprawdz<T: AsRef<[u8]>>(dane: T) -> bool {
    poprawny_naglowek(dane.as_ref())
}
fn main() {
    assert!(sprawdz(&b"RUSTx"[..]));
    assert!(sprawdz(vec![b'R', b'U', b'S', b'T']));
    assert!(!sprawdz(&b"RU"[..]));
}
~~~

Cięższa walidacja może rosnąć w niegenerycznym rdzeniu. Wrapper pozostaje ergonomiczny dla kolekcji, ale funkcja nie obiecuje zmniejszenia czasu wykonania bez pomiaru. Dla dużych danych unikaj przyjmowania posiadanej kolekcji, jeśli wywołujący potrzebuje jej później; przekazanie `&Vec<u8>` lub slice nie przenosi bufora.

## C12-3

Wybierz reprezentatywny zestaw typów pluginów i ten sam workload. Zmierz czysty build, build po zmianie jednego pluginu, szczyt pamięci kompilatora, rozmiar sekcji tekstowej i symboli, czas startu oraz p99 ścieżki wywołania. Potwierdź testami zgodność błędów i kolejności skutków. Oddziel koszt dynamic dispatch od ewentualnej nowej alokacji `Box`; można użyć pożyczonych obiektów traitu, jeśli model własności pozwala.

Wariant `dyn` akceptuj dopiero po spełnieniu uprzednio ustalonych progów, np. znacząco krótszy build przy dopuszczalnym wzroście p99. Zachowaj adapter umożliwiający wycofanie zmiany bez modyfikacji kontraktu pluginów. Nie utrzymuj obu implementacji bez potrzeby po rozstrzygnięciu eksperymentu, ale zachowaj dane i benchmark do ponownej oceny po aktualizacji toolchainu.
