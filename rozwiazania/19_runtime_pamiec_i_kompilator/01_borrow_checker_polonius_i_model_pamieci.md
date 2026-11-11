[← Spis treści](../../README.md)

# Rozwiązania: Borrow checker i model pamięci

## C09-1

~~~rust
fn main() {
    let mut a = vec![1, 2];
    let r = &a[0];
    assert_eq!(*r, 1);
    a.push(3);

    let mut b = vec![1, 2];
    let wartosc = b[0];
    b.push(3);
    assert_eq!(wartosc, 1);
}
~~~

Pierwsza wersja odczytuje przez pożyczkę przed modyfikacją; druga posiada kopię liczby i może jej użyć później. Gdy operacja zmienia pierwszy element, kopia zachowuje stary stan, natomiast ponowny odczyt z kolekcji da nowy. Dla typu niebędącego `Copy` trzeba świadomie wybrać pożyczkę, przeniesienie albo koszt klonowania.

## C09-2

~~~rust
fn zwieksz_brzegi(dane: &mut [i32]) {
    if let Some((pierwszy, reszta)) = dane.split_first_mut() {
        *pierwszy += 1;
        if let Some(ostatni) = reszta.last_mut() { *ostatni += 1; }
    }
}
fn main() {
    let mut pusty = [];
    zwieksz_brzegi(&mut pusty);
    let mut jeden = [4];
    zwieksz_brzegi(&mut jeden);
    assert_eq!(jeden, [5]);
    let mut wiele = [1, 2, 3];
    zwieksz_brzegi(&mut wiele);
    assert_eq!(wiele, [2, 2, 4]);
}
~~~

Kontrakt rozwiązania zwiększa jednoelementowy slice raz. `split_first_mut` wydziela pierwszy element i rozłączny ogon; `last_mut` działa wyłącznie na ogonie. Jeśli wartości mogą osiągnąć `i32::MAX`, trzeba dodatkowo ustalić politykę przepełnienia, np. `checked_add` z błędem albo saturację.

## C09-3

Wszystkie trzy wnioski są nieuprawnione. Borrow checker sprawdza pożyczki i przeniesienia w swoim zakresie, lecz raw pointer może wskazywać zwolnioną pamięć, a deklaracja FFI może mieć zły ABI. Miri bada wykonane ścieżki i przyjęty model; brak znalezionego kontrprzykładu nie obejmuje wszystkich indeksów, panik i przeplotów. Akceptacja na nightly nie zobowiązuje przyszłego stable: funkcja eksperymentalna, flagi i diagnostyka mogą się zmienić. Każde stwierdzenie o wsparciu powinno wskazywać rzeczywistą wersję, edycję i konfigurację, na której kod sprawdzono.
