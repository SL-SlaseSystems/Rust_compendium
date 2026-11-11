[← Spis treści](../README.md)
<!-- status: expanded -->

# Formaty danych, serializacja i walidacja granic

## Cele

Po tym rozdziale potrafisz:

- oddzielić model transportowy od niezmienników domeny;
- zaprojektować zgodną zmianę pola i reprezentacji enumu;
- odczytać ograniczoną ramkę binarną bez utożsamiania jej z layoutem struktury.

## Model — Format jest kontraktem w czasie

Serializacja przekształca wartości w reprezentację wymiany. Deserializacja odtwarza dane zgodne z formatem, lecz nie gwarantuje poprawności biznesowej. Obiekt `ZamowienieDto { ilosc: i64 }` może poprawnie odczytać `-4`; dopiero konstruktor `Ilosc` ma to odrzucić. Osobny DTO ułatwia obsługę starszych wersji i daje kontrolę nad tym, które pola wewnętrzne stają się publiczne.

**Third-party:** Serde definiuje wspólny model danych oraz traity `Serialize` i `Deserialize`; JSON, TOML i formaty binarne dostarczają własne implementacje formatu. Samo `#[derive(Serialize)]` nie wybiera JSON. Model oraz różnice między danymi posiadanymi i pożyczonymi sprawdzono 2026-11-11 w [Serde data model](https://serde.rs/data-model.html).

Zmiana nazwy pola Rust może niepotrzebnie zmienić protokół, jeżeli nazwa na drucie jest automatycznie wyprowadzana. Jawne `rename` stabilizuje zewnętrzne API. `alias` akceptuje dodatkową nazwę przy odczycie, natomiast `default` uzupełnia brakujące pole; nie naprawia dowolnej niepoprawnej wartości. Ustal, czy brak, `null` oraz pusta kolekcja znaczą to samo. Dla aktualizacji częściowej potrzebne bywa rozróżnienie trzech stanów: nie zmieniaj, usuń wartość, ustaw nową.

## Zgodna ewolucja JSON

**Third-party:** szkic wymaga Serde 1 z derive i wybranego serializatora. Nie jest doctestem i nie wykonuje odczytu pliku. Kontrakty atrybutów sprawdzono w [field attributes](https://serde.rs/field-attrs.html), 2026-11-11.

~~~text
#[derive(serde::Serialize, serde::Deserialize)]
struct ProfilDto {
    #[serde(rename = "display_name", alias = "name")]
    nazwa: String,
    #[serde(default)]
    etykiety: Vec<String>,
}
~~~

Nowy odbiorca przyjmie dawny klucz `name`, ale zapisze `display_name`. To zgodność nowego czytelnika ze starym dokumentem; nie dowodzi, że stary odbiorca zrozumie nowy zapis. Jeżeli musi, najpierw zmień odbiorców albo utrzymuj osobny serializer starej wersji. Nie dodawaj automatycznie `default` do pola krytycznego, np. waluty, gdy brak danych powinien zatrzymać operację.

Dla enumów jawny tag ogranicza niejednoznaczność. Reprezentacja `untagged` próbuje warianty w kolejności, więc dopisanie szerszego wariantu może zmienić interpretację starych danych. `tag` i `content` pozwalają ustabilizować nazwę zdarzenia i payload. Wybór zależy także od wsparcia formatu oraz alokacji. Zweryfikowano 2026-11-11 w [Serde enum representations](https://serde.rs/enum-representations.html). Wersję formatu warto umieścić w zewnętrznej kopercie, jeśli migracja wymaga innej interpretacji tych samych pól.

## Binarny format nie jest pamięcią obiektu

`repr(C)` nie określa endianness protokołu, wersji, długości ani znaczenia paddingu. Nie zapisuj bajtów `String` lub `Vec` jako trwałego formatu: zawierają stan procesu. Nawet prostą strukturę bez wskaźników koduj przez jawne pola. Zdefiniuj jednostkę długości, maksymalny rozmiar, dopuszczalne flagi i regułę dodatkowych bajtów.

~~~rust
fn payload(ramka: &[u8], max: usize) -> Result<&[u8], &'static str> {
    let naglowek: [u8; 4] = ramka.get(..4)
        .ok_or("brak długości")?.try_into().unwrap();
    let n = usize::try_from(u32::from_le_bytes(naglowek))
        .map_err(|_| "długość poza zakresem")?;
    if n > max { return Err("przekroczony limit"); }
    let koniec = 4_usize.checked_add(n).ok_or("przepełnienie")?;
    if ramka.len() != koniec { return Err("zła długość ramki"); }
    Ok(&ramka[4..koniec])
}
fn main() {
    assert_eq!(payload(&[2, 0, 0, 0, 10, 20], 8), Ok(&[10, 20][..]));
    assert_eq!(payload(&[9, 0, 0, 0], 8), Err("przekroczony limit"));
    assert!(payload(&[1, 0, 0, 0], 8).is_err());
}
~~~

Parser nie alokuje według niezaufanej długości. `get` sprawdza dostęp do nagłówka, `try_from` przenośnie konwertuje długość, a `checked_add` chroni obliczenie końca. `unwrap` dotyczy wyłącznie konwersji slice o już sprawdzonej długości czterech bajtów. Wymagamy dokładnie jednej ramki; parser strumieniowy powinien zamiast tego zwracać także liczbę zużytych bajtów i odróżniać niepełny input od błędu.

## Diagnostyka kompilatora

Typ z `Deserialize<'de>` może pożyczać z wejściowego bufora. Próba zwrócenia go po zniszczeniu lokalnej `String` zostanie odrzucona: dane nadal wskazują do źródła. Zwróć posiadany DTO albo przechowuj bufor poza funkcją i powiąż lifetimes. Zero-copy nie oznacza zerowej retencji pamięci: drobny widok może zatrzymać duży bufor.

Jeśli derive narzeka na atrybut lub nieobsługiwany wariant, sprawdź reprezentację. Przykładowo wewnętrzne tagowanie nie obsługuje dowolnych wariantów tuple. `deny_unknown_fields` przydaje się do konfiguracji, bo ujawnia literówki, ale utrudnia rozbudowę komunikatów wymienianych przez różne wersje. Nie łącz go z `flatten` wbrew ograniczeniom [container attributes](https://serde.rs/container-attrs.html), sprawdzonym 2026-11-11.

## Praktyka produkcyjna

Ogranicz rozmiar dokumentu, głębokość, liczbę rekordów i wynik dekompresji przed kosztowną walidacją. Obsłuż dane ucięte oraz nadmiarowe, a błędy opisuj ścieżką pola i kategorią bez kopiowania całego payloadu do logu. Dla podpisów i hashy ustal kanoniczną reprezentację; dwa semantycznie równe JSON-y mogą mieć różne bajty i kolejność pól.

Round-trip test wykryje część błędów, lecz serializer i deserializer mogą dzielić ten sam błąd. Zachowaj wzorcowe dokumenty poprzednich wersji i testy między niezależnymi implementacjami. Zmiana ustawień biblioteki binarnej, rozmiaru liczby lub kolejności pól może wymagać migracji nawet przy niezmienionej strukturze Rust. Koszt formatu oceniaj przez rozmiar, czas parsowania, alokacje i możliwość ręcznej diagnozy, a nie samą długość pliku.

## Sprawdź, czy rozumiesz

- Czy `alias` daje zgodność starego odbiorcy z nowym nadawcą?
- Dlaczego poprawny round-trip nie dowodzi zgodności protokołu?
- Kiedy pożyczony DTO zatrzyma więcej pamięci niż DTO posiadający krótkie pole?

## Ćwiczenia

- `C07-1` — podstawowe: Określ wynik odczytu starego i nowego pola nazwy oraz wynik zapisu szkicu ProfilDto. Wyjaśnij ograniczenie alias. [Rozwiązanie](../rozwiazania/18_serializacja_konfiguracja_i_integracje/01_formaty_serializacja_i_walidacja.md#c07-1).
- `C07-2` — praktyczne: Rozszerz zestaw testów payload o nagłówek krótszy niż 4, pusty payload, dodatkowy bajt oraz długość dokładnie równą limitowi. [Rozwiązanie](../rozwiazania/18_serializacja_konfiguracja_i_integracje/01_formaty_serializacja_i_walidacja.md#c07-2).
- `C07-3` — pogłębione: Zaprojektuj wersjonowaną kopertę zdarzenia ZamowienieUtworzone i migrację kwoty z tekstu na jednostki najmniejsze. Podaj walidację i test starego dokumentu. [Rozwiązanie](../rozwiazania/18_serializacja_konfiguracja_i_integracje/01_formaty_serializacja_i_walidacja.md#c07-3).

## Powiązane tematy

- [Konfiguracja i odporność](02_konfiguracja_sekrety_i_odpornosc_integracji.md)
- [HTTP i DTO](../16_web_i_api/01_http_routing_stan_i_bledy.md)
- [Layout pamięci](../21_unsafe_soundness_i_model_pamieci/03_layout_alignment_i_uninitialized_memory.md)
