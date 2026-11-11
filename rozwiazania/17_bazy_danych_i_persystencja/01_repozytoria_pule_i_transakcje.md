[← Spis treści](../../README.md)

# Rozwiązania: Repozytoria i transakcje

## C05-1

~~~rust
fn main() {
    assert_eq!(-1_i64 as u32, u32::MAX);
    assert!(u32::try_from(-1_i64).is_err());
    assert_eq!(u32::try_from(u32::MAX as i64), Ok(u32::MAX));
    assert!(u32::try_from(u32::MAX as i64 + 1).is_err());
}
~~~

Po konwersji zakresu konstruktor `Ilosc` nadal musi odrzucić `0`. `TryFrom<i64> for u32` sprawdza reprezentację liczbową, a nie domenową dodatniość.

## C05-2

A i B czytają `stan=10`. Oba uznają 7 za dostępną ilość. Jeśli oba zapisują obliczone lokalnie `3`, system zaakceptował rezerwacje na 14, a stan sugeruje zużycie tylko 7. Jeśli bezwarunkowo odejmują 7 w bazie, drugi może naruszyć CHECK albo uzyskać stan ujemny bez ograniczenia.

Warunkowy `UPDATE` modyfikuje wiersz tylko wtedy, gdy aktualny stan wystarcza. W PostgreSQL konkurujący updater po oczekiwaniu ponownie ocenia warunek na zaktualizowanym wierszu. Pierwszy zmienia 10 na 3, drugi nie aktualizuje żadnego wiersza. Oczekiwane: jeden sukces, jedna odmowa, stan końcowy 3. Test wymaga dwóch połączeń i rzeczywistej współbieżności; sekwencyjne wywołania nie odtwarzają podatnego przeplotu.

## C05-3

Tabela operacji ma unikalny klucz `(tenant_id, klucz)` oraz fingerprint parametrów, stan i wynik. W transakcji najpierw zarezerwuj klucz przez insert z obsługą konfliktu. Tylko zwycięzca wykonuje warunkową rezerwację, zapisuje jej wynik i wpisuje zdarzenie do outboxu. Pozostałe wywołanie odczytuje zatwierdzony wynik; ten sam klucz z innymi parametrami daje konflikt, a nie drugą rezerwację. Wszystkie zmiany zatwierdzają się razem.

Po zerwaniu podczas commit klient ponawia ten sam klucz, zamiast tworzyć nowy. Jeśli commit się udał, otrzyma poprzedni wynik; jeśli nie, może wykonać operację. Worker publikuje outbox po commit i może wysłać zdarzenie ponownie po awarii między publikacją a oznaczeniem wysłania. Odbiorca deduplikuje po identyfikatorze zdarzenia. Rejestr kluczy potrzebuje okresu retencji zgodnego z oknem retry, a fingerprint nie powinien ujawniać sekretów.
