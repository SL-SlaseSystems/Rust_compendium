[← Spis treści](../README.md)
<!-- status: expanded -->

# Tablice, wektory i sekwencje

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- dobrać sekwencję do operacji na końcach, środku i priorytetach;
- rozróżnić długość od pojemności oraz utratę stabilności referencji;
- zaplanować usuwanie elementów z uwzględnieniem wymaganej kolejności;

## Model — układ danych i profil operacji


Dobór kolekcji opisuje oczekiwane operacje, nie tylko „wiele elementów”.

## Tablica, slice i wektor

- `[T; N]` — długość stała w typie, dane zwykle inline;
- `&[T]` — pożyczony widok na ciągły fragment;
- `Vec<T>` — posiadany, ciągły bufor o zmiennej długości.

~~~rust
fn odwroc(dane: &mut [i32]) {
    dane.reverse();
}

fn main() {
    let tablica = [1, 2, 3];
    let mut wektor = Vec::with_capacity(4);
    wektor.extend_from_slice(&tablica);
    wektor.push(4);
    odwroc(&mut wektor);
    assert_eq!(wektor, [4, 3, 2, 1]);
    assert!(wektor.capacity() >= wektor.len());
}
~~~

`Vec` ma długość i pojemność. `push` może realokować, więc referencje do
elementów nie mogą pozostawać aktywne podczas mutacji wektora.

`get(index)` zwraca `Option<&T>`; indeksowanie `v[index]` powoduje panic poza
zakresem. `swap_remove` usuwa w O(1), ale zmienia kolejność. `remove` zachowuje
kolejność kosztem przesunięcia końcówki.

## `VecDeque<T>`

Dwukierunkowa kolejka wspiera tanie dodawanie i zdejmowanie na obu końcach:

~~~rust
use std::collections::VecDeque;

fn main() {
    let mut q = VecDeque::new();
    q.push_back("drugie");
    q.push_front("pierwsze");
    assert_eq!(q.pop_front(), Some("pierwsze"));
    assert_eq!(q.pop_back(), Some("drugie"));
}
~~~

Bufor może zawijać się w pamięci i składać z dwóch slices. Gdy potrzebujesz
jednego ciągłego obszaru, użyj `make_contiguous`.

## `LinkedList<T>`

Standardowa lista dwukierunkowa istnieje, ale rzadko przewyższa `Vec` lub
`VecDeque`. Dodatkowe alokacje i słaba lokalność cache często dominują nad
teoretycznym O(1) wstawiania. Wybieraj ją dopiero po pomiarze i gdy operacje
łączenia i dzielenia list rzeczywiście pasują.

## `BinaryHeap<T>`

Kopiec binarny jest kolejką priorytetową typu max-heap:

~~~rust
use std::collections::BinaryHeap;

fn main() {
    let mut zadania = BinaryHeap::from([2, 9, 4]);
    assert_eq!(zadania.pop(), Some(9));
    assert_eq!(zadania.peek(), Some(&4));
}
~~~

Do min-heap opakuj klucz w `std::cmp::Reverse`. Zmiana wartości wpływającej na
porządek, gdy jest w kopcu, jest błędem logicznym; bezpieczne API ogranicza
możliwość takiej mutacji.

## Złożoność i pamięć

Notacja O opisuje wzrost, lecz nie stałe koszty i cache. `Vec` zwykle jest
najlepszym domyślnym wyborem dla sekwencji. Rezerwuj pojemność, jeśli znasz
przybliżony rozmiar, ale nie trzymaj ogromnego bufora „na wszelki wypadek”.

## Reguły — długość, pojemność i granice pamięci

Długość `Vec` to liczba zainicjalizowanych elementów dostępnych przez bezpieczne API. Pojemność to liczba miejsc, które bufor może pomieścić przed potrzebą wzrostu. `Vec::with_capacity(100)` nie tworzy stu elementów; indeks zero nadal jest błędny, dopóki nie dodasz wartości. `reserve` zwiększa pojemność, a `resize` zmienia długość i tworzy albo niszczy elementy.

`push` ma koszt amortyzowany O(1), ale pojedynczy wzrost może realokować i przenieść cały bufor. Nie obiecuj stałego opóźnienia każdej operacji na tej podstawie. `with_capacity(n)` gwarantuje co najmniej żądaną pojemność, a nie określony współczynnik wzrostu wektora. Dla typów zero-sized zasady alokacji i raportowana pojemność są szczególne; nie wnioskuj z liczby elementów o liczbie zaalokowanych bajtów.

~~~rust
fn usun_nieparzyste(dane: &mut Vec<u32>) {
    dane.retain(|n| n % 2 == 0);
}
fn main() {
    let mut dane = vec![4, 1, 6, 3, 8];
    usun_nieparzyste(&mut dane);
    assert_eq!(dane, [4, 6, 8]);
    let pojemnosc = dane.capacity();
    dane.clear();
    assert_eq!(dane.len(), 0);
    assert_eq!(dane.capacity(), pojemnosc);
}
~~~

`retain` zachowuje względną kolejność elementów pozostawionych. Nie wymaga usuwania indeksów podczas iteracji, które łatwo prowadzi do pominięcia elementu po przesunięciu. `clear` niszczy elementy, lecz zachowuje bufor do ponownego użycia. W serwisie wielokrotnie przetwarzającym paczki to oszczędza alokacje; przy jednorazowym ogromnym żądaniu może niepotrzebnie zatrzymać pamięć przez resztę życia procesu.

## Dobór sekwencji według kontraktu

Jeżeli kolejka wykonuje `push_back` i `pop_front`, `VecDeque` pozwala uniknąć przesuwania całego prefiksu, którego wymaga `Vec::remove(0)`. Iterator zachowuje kolejność logiczną, choć dane mogą zajmować dwa fizyczne fragmenty. `make_contiguous` scala widok kosztem potencjalnego przestawienia elementów; uwzględnij ten koszt przy granicy z API wymagającym slice.

`BinaryHeap` daje dostęp do maksimum, lecz jego zwykła iteracja nie zwraca elementów w porządku sortowania. Kolejność uzyskujesz przez powtarzane `pop` albo odpowiednią konwersję. `Reverse` odwraca porządek, nie zmieniając algorytmu kopca. Priorytet złożony warto zapisać w osobnym kluczu; porównanie musi być spójne przez cały pobyt elementu w kopcu.

`LinkedList` nie usuwa kosztu znajdowania pozycji. O(1) dla przepięcia znanych węzłów nie oznacza O(1) dla „wstaw na pozycji milion”. Rzeczywisty benchmark powinien uwzględniać alokacje, przejście do miejsca i lokalność danych. Domyślne użycie `Vec` jest rozsądne, dopóki wymagania nie wskazują konkretnej przewagi innej reprezentacji.

## `array::from_fn`: element zależny od indeksu

`std::array::from_fn` tworzy `[T; N]`, wywołując `FnMut(usize) -> T` dla indeksów od zera do `N - 1`. Długość wynika z typu docelowego lub parametru const, a wynik jest tablicą, nie leniwym iteratorem. To prosty sposób konstruowania elementów nieimplementujących `Copy` i wartości zależnych od indeksu. Dla `N == 0` closure nie jest wywoływana.

~~~rust
fn main() {
    let mut odwiedzone = Vec::new();
    let bufory: [String; 3] = std::array::from_fn(|i| {
        odwiedzone.push(i);
        format!("bufor-{i}")
    });
    assert_eq!(odwiedzone, [0, 1, 2]);
    assert_eq!(bufory[2], "bufor-2");
    let pusta: [String; 0] = std::array::from_fn(|_| panic!("nie wywołano"));
    assert!(pusta.is_empty());
}
~~~

Powtórzenie `[wartosc; N]` i konstrukcja przez `from_fn` mają inne wymagania i moment ewaluacji. Closure może mutować przechwycony licznik, ale skutek poza tablicą nie zostanie cofnięty przy panice konstruktora. Korzystaj z bezpiecznego API zamiast ręcznie budować tablicę niezainicjalizowanych `String`; do inicjalizacji w kontekście const sprawdź osobno dostępność operacji — zwykła stabilność `from_fn` nie oznacza stabilnego `const from_fn`. Dokumentacja: [array::from_fn](https://doc.rust-lang.org/std/array/fn.from_fn.html).

## Diagnostyka kompilatora

Referencja do elementu nie może pozostać używana po potencjalnie realokującej mutacji wektora. Zapas pojemności nie zmienia statycznego kontraktu `push`.

~~~compile_fail
fn main() {
    let mut dane = Vec::with_capacity(10);
    dane.push(String::from("A"));
    let pierwszy = &dane[0];
    dane.push(String::from("B"));
    println!("{pierwszy}");
}
~~~

E0502 naprawisz przez zakończenie używania referencji przed `push`, przechowanie stabilnego identyfikatora zamiast pożyczki albo zmianę reprezentacji. Skopiowanie małego `Copy` może wystarczyć. Indeks pozostaje liczbą po realokacji, ale usunięcie lub przestawienie elementów może zmienić jego znaczenie; nie jest uniwersalną trwałą tożsamością.

## Praktyka produkcyjna

Ogranicz maksymalną liczbę i rozmiar elementów z wejścia. `try_reserve` pozwala obsłużyć błąd konkretnej rezerwacji jako `Result`, lecz dalsze operacje nie stają się od tego automatycznie nieomylne. Waliduj sumy i mnożenia rozmiarów przez `checked_*` przed rezerwowaniem bufora.

Wybierz stabilność kolejności przed optymalizacją usuwania: `swap_remove` zmienia porządek i indeksy, `remove` przesuwa ogon, a `retain` filtruje całość z zachowaniem kolejności. W wynikach widocznych dla użytkownika zmiana kolejności może być błędem produktu mimo poprawy benchmarku. Testuj zarówno wynik, jak i wymaganą kolejność.

## Sprawdź, czy rozumiesz

1. Dlaczego rezerwacja pojemności nie pozwala indeksować niezainicjalizowanych elementów?
2. Czy iteracja po `BinaryHeap` daje posortowane dane?
3. Kiedy `swap_remove` łamie kontrakt aplikacji?

## Ćwiczenia

- `A24-1` — podstawowe: utwórz wektor z pojemnością co najmniej 4, dodaj dwa elementy i porównaj długość z pojemnością [Rozwiązanie](../rozwiazania/06_kolekcje_iteratory_i_closures/01_tablice_wektory_i_sekwencje.md#a24-1).
- `A24-2` — praktyczne: zbuduj kolejkę FIFO dla trzech zadań przez `VecDeque` i sprawdź kolejność odbioru [Rozwiązanie](../rozwiazania/06_kolekcje_iteratory_i_closures/01_tablice_wektory_i_sekwencje.md#a24-2).
- `A24-3` — pogłębione: utwórz kolejkę priorytetową minimum przez `BinaryHeap<Reverse<u32>>`; opróżnij ją w rosnącej kolejności [Rozwiązanie](../rozwiazania/06_kolekcje_iteratory_i_closures/01_tablice_wektory_i_sekwencje.md#a24-3).

## Źródła i zakres stabilności

Kontrakty długości, pojemności i wzrostu: [Vec](https://doc.rust-lang.org/std/vec/struct.Vec.html). Dobór struktur: [std::collections](https://doc.rust-lang.org/std/collections/index.html). Porządek kopca: [BinaryHeap](https://doc.rust-lang.org/std/collections/struct.BinaryHeap.html).

## Powiązane tematy

- [Slices i `str`](../03_ownership_i_pamiec/04_slices_i_str.md)
- [Mapy i zbiory](03_mapy_zbiory_i_entry.md)
- [Iteratory](05_iteratory.md)
