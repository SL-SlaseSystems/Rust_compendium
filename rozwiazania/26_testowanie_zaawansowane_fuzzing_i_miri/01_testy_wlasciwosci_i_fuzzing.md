[← Spis treści](../../README.md)

# Rozwiązania: Testy właściwości, generatory i fuzzing

[Rozdział źródłowy](../../26_testowanie_zaawansowane_fuzzing_i_miri/01_testy_wlasciwosci_i_fuzzing.md)

## D05-1

Wynik jest niemalejący, a liczność każdego elementu jest zachowana. Sama zgodność długości nie wykrywa podmiany elementów, a sama monotoniczność nie wykrywa zgubionego elementu. Dodaj pusty wektor, duplikaty i wartości skrajne.

## D05-2

Klucz jest niepusty i nie zawiera separatora, wartość może być pusta oraz zawierać kolejne `=`. Ogranicz długości obu części, a osobno generuj Unicode. Zbuduj model przed kodowaniem, potem porównuj wynik parsera z tym modelem. Oddzielna strategia błędna obejmuje brak separatora i pusty klucz.

## D05-3

Dla tych samych bajtów i każdego wybranego punktu cięcia przetworzenie prefiksu, potem sufiksu daje tę samą sekwencję rekordów i błąd końcowy co całość. Należy jawnie zakończyć strumień, aby odróżnić niepełną ramkę od danych oczekujących na resztę. Ogranicz liczbę podziałów dla dużych wejść.
