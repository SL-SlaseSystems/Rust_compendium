[← Spis treści](../../README.md)

# Rozwiązania: Layout i inicjalizacja

## C15-1

Po `wez` właścicielem jest zwrócone `Some(String)`. Slot ma `pelny=false`, więc nie niszczy starej reprezentacji. Gdy wynik wychodzi z zakresu, normalny drop zwalnia bufor napisu. Jeśli `wez` nie było, `Slot::drop` wykonuje `assume_init_drop` dokładnie raz. Sam `MaybeUninit<T>` nie wykonuje `T::drop`, niezależnie od poprzednich zapisów. Pusty slot nie niszczy żadnego `T`.

## C15-2

Typ testowy posiada `Rc<Cell<usize>>` i w `Drop` zwiększa licznik. Dla pełnego slota z jedną wartością po końcu zakresu oczekuj 1. Dla `wez` licznik pozostaje 0 po zniszczeniu pustego slota i rośnie do 1 dopiero po zniszczeniu wyniku. Przy `wstaw(a)`, `wez`, `wstaw(b)` zniszcz wynik `a` i slot; końcowy licznik to 2. Drugie `wez` z pustego slota nie zmienia licznika.

Szkic asercji wymaga dołączenia typu Slot z rozdziału, więc nie jest samodzielnym doctestem:

~~~text
let wynik = slot.wez().unwrap();
drop(slot);
assert_eq!(licznik.get(), 0);
drop(wynik);
assert_eq!(licznik.get(), 1);
~~~

Test potwierdza obserwowane ścieżki. Dowód nadal wymaga, że flaga odpowiada inicjalizacji dla każdego `T`, w tym ZST i typów z panikującym destructorem.

## C15-3

Guard posiada magazyn `[MaybeUninit<T>; N]` i liczbę `init` z niezmiennikiem: dokładnie elementy `0..init` zawierają żywe T. Każdy przebieg najpierw tworzy nową wartość, następnie zapisuje ją przez `write`, a na końcu zwiększa `init`, bez panikującej operacji między zapisem i licznikiem. Jeżeli konstruktor k-tej wartości panikuje przed zapisem, guard niszczy tylko poprzedni prefix; nie dotyka niezainicjalizowanych miejsc.

Po sukcesie przeniesienie całej tablicy musi przekazać własność dokładnie raz. Rozbrojenie guarda i odczyt do `[T; N]` wymagają protokołu bez punktu paniki, który mógłby spowodować podwójny drop. Nie wolno pozostawić `init=N` w guardzie po przekazaniu elementów wynikowi. Prostsza implementacja produkcyjna to `std::array::from_fn`, jeśli konstrukcja nie wymaga szczególnego fallible API; dla wyniku z błędem często wystarcza Vec ze sprawdzoną długością i konwersją.
