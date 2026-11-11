[← Spis treści](../../README.md)

# Rozwiązania: Bezpieczne otoczki FFI

## C17-1

Dwa obiekty uznałyby się za wyłącznych właścicieli. Pierwszy Drop zwolni Raw, drugi get odczyta zwolnioną pamięć albo drugi Drop zwolni ją ponownie. Kopia pointera nie jest nowym zasobem. Alternatywy: nie implementować Clone, wywoływać obcą funkcję tworzącą niezależną kopię albo korzystać z udokumentowanego refcountu obcej biblioteki i pary retain/release. `Arc<Handle>` dzieli jednego właściciela po stronie Rust, lecz nadal wymaga odpowiedniego kontraktu wątkowego dla współdzielonych wywołań.

## C17-2

Dla cap 0 wynik to 0 i pętla nie wykonuje dostępu; dla cap 2 zapisuje dokładnie bajty 0 i 1, wynik 2; dla cap 8 zapisuje 0, 1, 2 i zwraca 3. `set_len(n)` jest dopuszczalne dopiero po potwierdzeniu, że te miejsca zostały zainicjalizowane i producent respektował cap. Dla `u8` każdy ustalony bit pattern jest poprawny. Puste wywołanie nadal musi odpowiadać rzeczywistemu kontraktowi obcego API: nasza symulacja nie wymaga dereferencjonowania pointera przy cap 0, ale inna funkcja może wymagać konkretnego sentinela lub non-null.

## C17-3

Context posiada stan `aktywny/zamykany`, licznik aktywnych callbacków i synchronizację. Rejestracja przekazuje stabilny adres posiadanej alokacji. Callback najpierw wchodzi do protokołu, odmawia nowej pracy po zamykaniu, zwiększa licznik, wykonuje pracę i zmniejsza licznik przez guard także przy unwind. Trampoline przechwytuje dopuszczalną panikę przed granicą `extern "C"` i zamienia ją na udokumentowany wynik.

Zamykanie blokuje nowe callbacki w API producenta, wywołuje unregister i czeka na potwierdzenie oraz licznik 0. Dopiero wtedy zwalnia context dokładnie raz. Jeśli obca biblioteka nie gwarantuje atomowego końca rejestracji, sam licznik może mieć wyścig między sprawdzeniem a wejściem callbacku; potrzebny jest silniejszy kontrakt producenta. Ustal też reentrancy: zamykanie z wnętrza callbacku nie może czekać na własny licznik. W przypadku zapomnienia ownera dopuszczalny jest wyciek posiadanego contextu, lecz nie wskaźnik do wygasłego stosu.
