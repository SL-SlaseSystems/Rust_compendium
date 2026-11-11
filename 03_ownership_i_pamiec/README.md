[← Spis treści](../README.md)

# 3. Ownership i pamięć

## Dla kogo i po co

Dla każdego użytkownika Rust. Ten dział buduje model własności zasobów, na którym opierają się bezpieczeństwo pamięci, współbieżność i projektowanie API.

## Wymagania wstępne

Podstawy typów, funkcji i sterowania przepływem.

## Kolejność materiałów

1. [Stos, sterta i RAII](01_stos_sterta_i_raii.md)
2. [Ownership, move i `Copy`](02_ownership_move_i_copy.md)
3. [Referencje i borrowing](03_referencje_i_borrowing.md)
4. [Slices i `str`](04_slices_i_str.md)
5. [Lifetimes](05_lifetimes.md)
6. [Smart pointery i interior mutability](06_smart_pointery_i_interior_mutability.md)

## Po tym dziale

Potrafisz przewidywać przeniesienia wartości, projektować pożyczki i dobierać smart pointer do rzeczywistego modelu współdzielenia.

## Jak pracować z działem

Rysuj osobno właścicieli i pożyczki. W pierwszych dwóch rozdziałach śledź, kto odpowiada za zniszczenie bufora. W kolejnych dwóch określ, kto może w danym momencie odczytywać lub zmieniać dane oraz czy widok może przeżyć właściciela. Dopiero wtedy przejdź do nazwanych lifetimes i struktur współwłasności.

Zestawy ćwiczeń `A10`–`A15` prowadzą od rozmiaru nagłówka oraz kolejności `Drop` przez pobieranie pól i rozdzielanie slice do grafu z `Weak`. Rozwiązania zawierają kompletne programy i wyjaśniają ważne granice: guard ma własny czas życia, `clone` nie zawsze tworzy niezależne dane, a `Arc` nie dodaje dowolnej mutacji.

## Punkt kontrolny

Potrafisz rozwiązać E0382, E0499 i E0502 przez zmianę kontraktu lub faz operacji, bez odruchowego klonowania kolekcji. Umiesz zaprojektować parser zwracający pożyczony fragment oraz wariant posiadający wynik dla kolejki. Wyjaśniasz, dlaczego krótka pożyczka i moment destrukcji właściciela to dwie odrębne kwestie.

Nie musisz implementować własnego smart pointera. Gotowość do kolejnego działu oznacza świadome użycie bezpiecznych typów i rozpoznanie sytuacji, w której wymagane uprawnienia nie mieszczą się w obecnej sygnaturze.

## Co dalej

Przećwicz modelowanie danych przez struktury i enumy. Do lifetimes wracaj przy projektowaniu API, nie jako do mechanizmu „przedłużania życia” danych.

Następny dział: [Struktury, enumy i wzorce](../04_struktury_enumy_i_wzorce/README.md).
