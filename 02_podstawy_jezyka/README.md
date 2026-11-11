[← Spis treści](../README.md)

# 2. Podstawy języka

## Dla kogo i po co

Dla początkujących, którzy chcą swobodnie czytać i pisać małe programy Rust przed wejściem w ownership.

## Wymagania wstępne

Dział 1 oraz działające polecenia `cargo check`, `cargo run` i `cargo test`.

## Kolejność materiałów

1. [Zmienne, stałe i shadowing](01_zmienne_stale_i_shadowing.md)
2. [Typy i konwersje](02_typy_i_konwersje.md)
3. [Funkcje, wyrażenia i instrukcje](03_funkcje_wyrazenia_i_instrukcje.md)
4. [Sterowanie przepływem](04_sterowanie_przeplywem.md)
5. [Operatory, komentarze i atrybuty](05_operatory_komentarze_i_atrybuty.md)

## Po tym dziale

Umiesz wyrażać obliczenia za pomocą typów, funkcji, bloków i kontroli przepływu oraz interpretować podstawowe błędy kompilatora.

## Jak pracować z działem

Kolejność prowadzi od nazwania wartości przez reprezentację danych do granic funkcji i decyzji sterowania. Przy każdym przykładzie najpierw zapisz typ wyniku. Dopiero potem uruchom kod: część najważniejszych różnic, takich jak końcowy średnik albo stratne `as`, nie jest widoczna w samej nazwie zmiennej.

Rozdziały o bindingach, liczbach i funkcjach zachowują zadania `P01`–`P03`. Sterowanie przepływem oraz operatory dodają zadania `A08` i `A09`. Każdy zestaw ma poziom podstawowy, praktyczny oraz pogłębiony i prowadzi do konkretnego rozwiązania. Celowo niekompilujące się przykłady tłumaczą rodzaj naruszonego kontraktu; nie traktuj ich jako kodu do kopiowania do programu.

## Punkt kontrolny

Napisz funkcję przyjmującą tekst liczbowy, jawnie wybierającą typ oraz regułę błędu, a następnie przetwórz kilka wartości pętlą bez ręcznego indeksowania. Wyjaśnij, które działania konsumują dane, co daje `()` i dlaczego przepełnienie nie może zależeć od niejawnego założenia o profilu.

Do następnego działu przejdź, gdy potrafisz oddzielić binding, wartość i referencję oraz opisać warunek zakończenia pętli. Nie musisz jeszcze znać formalnych adnotacji lifetime.

## Co dalej

Przejdź do ownership i pamięci — to centralny model, który nadaje sens większości reguł Rust.

Następny dział: [Ownership i pamięć](../03_ownership_i_pamiec/README.md).
