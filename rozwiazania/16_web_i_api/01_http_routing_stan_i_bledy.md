[← Spis treści](../../README.md)

# Rozwiązania: HTTP i model błędów

## C03-1

Przykładowy spójny kontrakt: niepoprawny JSON `400`/`niepoprawny_json`; pusta nazwa `422`/`pusta_nazwa`; zajęty login `409`/`login_zajety`; niedostępna baza `503`/`zaleznosc_niedostepna`. Body to np. `{"kod":"pusta_nazwa","request_id":"r-17"}`. Jeśli ujawnienie zajętego loginu pozwala wyliczać konta, polityka produktu może wymagać bardziej ogólnej odpowiedzi. Do klienta nie trafia adres bazy ani surowa treść błędu sterownika. `503` nie obiecuje, że dowolny zapis wolno ponowić bez idempotencji.

## C03-2

~~~rust
#[derive(Debug, PartialEq)]
struct UserId(u64);
impl TryFrom<u64> for UserId {
    type Error = &'static str;
    fn try_from(x: u64) -> Result<Self, Self::Error> {
        if x == 0 { Err("zerowy_id") } else { Ok(Self(x)) }
    }
}
fn main() {
    assert!(UserId::try_from(0).is_err());
    assert_eq!(UserId::try_from(1), Ok(UserId(1)));
}
~~~

`UserId(1)` jest poprawny składniowo i domenowo, lecz użytkownik wywołujący może nie mieć prawa czytać tego zasobu. Sprawdzenie właściciela lub roli następuje przy operacji, z tożsamością pochodzącą z uwierzytelnienia, a nie z dowolnego pola JSON.

## C03-3

Typ publiczny `BladBody { kod: &'static str, request_id: String }` serializuje się identycznie dla wszystkich ścieżek. Prywatny enum `ApiError` ma warianty `Walidacja`, `ZlyJson`, `NieZnaleziono`, `Konflikt`, `Infrastruktura`. Adapter `IntoResponse` ustala status, a wewnętrzna przyczyna infrastruktury jest wyłącznie logowana. Handler przyjmuje `Result<Json<DTO>, JsonRejection>` i zamienia odrzucenie na `ApiError::ZlyJson`; fallback routera zwraca ten sam `ApiError::NieZnaleziono`.

Testy wysyłają zły JSON, poprawne dane z pustą nazwą i nieistniejącą trasę. Dla każdego sprawdzają: właściwy status, JSON z polami `kod` i `request_id` oraz brak surowych danych błędu w body. Dodatkowo warto zapewnić, że odrzucenie JSON nie wywołało repozytorium: transport nie powinien wykonywać skutków po nieudanej ekstrakcji.
