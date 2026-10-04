[← Spis treści](../README.md)

# Pliki, I/O i procesy

Standardowe I/O opiera się na traits `Read`, `Write`, `BufRead` i `Seek`.
Funkcje wygodne wczytują całość; API strumieniowe kontroluje pamięć.

## Pliki

~~~rust
use std::fs::{self, File};
use std::io::{BufRead, BufReader, Write};

fn main() -> std::io::Result<()> {
    let sciezka = std::env::temp_dir().join("rust-kompendium-io.txt");
    {
        let mut plik = File::create(&sciezka)?;
        writeln!(plik, "pierwsza")?;
        writeln!(plik, "druga")?;
        plik.flush()?;
    }
    let plik = File::open(&sciezka)?;
    let linie: Result<Vec<_>, _> = BufReader::new(plik).lines().collect();
    assert_eq!(linie?, ["pierwsza", "druga"]);
    fs::remove_file(sciezka)?;
    Ok(())
}
~~~

`lines` usuwa zakończenie linii i wymaga poprawnego UTF-8. Dla protokołów
binarnych używaj `read`/`read_exact` na bajtach.

## Częściowe operacje

`Read::read` może zwrócić mniej bajtów niż bufor nawet przed EOF. `Write::write`
może zapisać część. `read_exact` i `write_all` realizują pętlę, lecz mają
własne zachowanie przy błędzie. `Interrupted` bywa sygnałem do retry.

Nie utożsamiaj pojedynczego `read` z jedną wiadomością protokołu.

## Ścieżki

`Path` i `PathBuf` nie muszą być UTF-8. Nie zamieniaj każdej ścieżki na
`String`. Używaj `display` tylko do komunikatu dla człowieka; wynik może być
stratny. Łączenie przez `join` jest przenośniejsze niż konkatenacja separatora.

## Atomowy zapis

Typowy wzorzec konfiguracji to zapis do pliku tymczasowego w tym samym
filesystemie, `flush`/ewentualnie `sync_all`, a potem rename. Gwarancje rename,
trwałości katalogu i nadpisania zależą od platformy. Biblioteka nie oferuje
uniwersalnej transakcji filesystemu.

## Procesy

~~~rust
use std::process::Command;

fn main() -> std::io::Result<()> {
    let wynik = Command::new("rustc").arg("--version").output()?;
    assert!(wynik.status.success());
    assert!(String::from_utf8_lossy(&wynik.stdout).contains("rustc"));
    Ok(())
}
~~~

`Command` nie uruchamia powłoki domyślnie, co ogranicza injection. Nie buduj
jednego łańcucha komendy z wejścia użytkownika. Przy `stdin/stdout(Stdio::piped())`
czytaj i zapisuj równolegle, aby nie zakleszczyć się na pełnych pipe’ach.

## Środowisko i kody wyjścia

`std::env::var_os` zachowuje nie-UTF-8. `ExitStatus` może nie mieć zwykłego
kodu, np. gdy proces zakończył sygnał. Proces potomny trzeba `wait`, inaczej
na części systemów pozostaje zombie.

## Powiązane tematy

- [`String`, `str` i Unicode](../06_kolekcje_iteratory_i_closures/02_string_str_i_unicode.md)
- [Sieć i protokoły](02_siec_i_protokoly.md)
- [Własne błędy](../07_obsluga_bledow/04_wlasne_bledy_i_api.md)
