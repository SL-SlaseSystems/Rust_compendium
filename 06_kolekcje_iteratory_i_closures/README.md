[← Spis treści](../README.md)

# 6. Kolekcje, iteratory i closures

## Dla kogo i po co

Dla osób przetwarzających dane w pamięci i chcących pisać kod deklaratywny bez ukrywania kosztów.

## Wymagania wstępne

Ownership, struktury, enumy, generics i podstawy traits.

## Kolejność materiałów

1. [Tablice, wektory i sekwencje](01_tablice_wektory_i_sekwencje.md)
2. [`String`, `str` i Unicode](02_string_str_i_unicode.md)
3. [Mapy, zbiory i Entry API](03_mapy_zbiory_i_entry.md)
4. [Closures i rodzina `Fn`](04_closures_i_fn_traits.md)
5. [Iteratory](05_iteratory.md)

## Po tym dziale

Potrafisz dobrać kolekcję, bezpiecznie obsłużyć tekst Unicode i budować potoki iteratorów o kontrolowanym ownership.

## Jak pracować z działem

Zacznij od profilu operacji na danych: rozmiaru, kolejności, wyszukiwania i modyfikacji. Potem oddziel bajty UTF-8 od wartości `char` oraz grafemów. Dopiero znając własność danych, przejdź do closure i leniwych iteratorów; wtedy typ `Item` i sposób capture przestają być ukrytymi szczegółami.

Zestawy `A24`–`A28` prowadzą od długości oraz pojemności wektora do kolejki priorytetowej, bezpiecznego prefiksu tekstu, deterministycznego raportu i własnego iteratora. Każde zadanie ma poziom oraz odsyłacz do pełnego rozwiązania. Rozwiązania opisują także to, czego dany kontrakt nie zapewnia: bajtowy prefiks może przerwać grafem, a porządek grup nie definiuje automatycznie porządku elementów wewnątrz grupy.

## Punkt kontrolny

Potrafisz dobrać `Vec`, `VecDeque`, `BinaryHeap`, `HashMap` lub `BTreeMap` według wymaganych operacji. Umiesz przewidzieć, kiedy callback potrzebuje `FnMut`, a kiedy `FnOnce`, i co zostanie skonsumowane przez iterator. Rozpoznajesz krótki obieg błędu bez mylenia go z wycofaniem wcześniejszych skutków.

Do obsługi błędów przejdź z umiejętnością zebrania `Iterator<Item = Result<T, E>>` do `Result<Vec<T>, E>` i wskazania granicy, na której należy dodać kontekst domenowy.

## Co dalej

Przejdź do obsługi błędów; `Option` i `Result` naturalnie łączą się z iteratorami i combinatorami.

Następny dział: [Obsługa błędów](../07_obsluga_bledow/README.md).
