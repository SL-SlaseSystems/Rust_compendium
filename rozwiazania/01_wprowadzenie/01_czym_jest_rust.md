[← Spis treści](../../README.md)

# Rozwiązania: Czym jest Rust

Poniższe odpowiedzi pokazują sposób uzasadniania decyzji. Nie są uniwersalnym rankingiem technologii: właściwy wybór zależy od mierzalnych ograniczeń projektu.

## W01-1

Rust jest uzasadniony dla CLI przetwarzającego milion wierszy, jeżeli pomiar potwierdza znaczenie trzech kryteriów: zużycia pamięci przy strumieniowym I/O, czasu wykonania w gorącej ścieżce oraz łatwej dystrybucji pojedynczego binarium. Typy i ownership pomagają też utrzymać poprawne zarządzanie buforami bez `GC`.

To nie jest rozstrzygnięcie z definicji. Jeżeli narzędzie jest jednorazową automatyzacją, a istniejące SDK domenowe i kompetencje zespołu skracają dostawę w innym środowisku, ten koszt może przeważyć. Przed decyzją warto porównać prototypy na reprezentatywnym pliku i zmierzyć czas, pamięć oraz koszt wdrożenia.

## W01-2

Bezpieczny Rust ogranicza klasę błędów pamięci i wyścigów danych, lecz nie daje gotowego protokołu usługi. Przykładowe ryzyko pozostające poza modelem typów to nieograniczony napływ żądań, który wyczerpuje kolejkę lub połączenia. Ogranicza się je limitem współbieżności, limitami czasu, kolejką o ograniczonej pojemności i obserwacją opóźnień oraz błędów.

Osobno trzeba zaprojektować autoryzację, semantykę ponowień i spójność z bazą danych. Rust może uczynić współdzielony stan trudniejszym do niewłaściwego użycia, ale nie wybiera poprawnej polityki ani nie zastępuje testów integracyjnych.

## W01-3

Dla komponentu z FFI wybrałbym Rust, gdy ograniczenie ryzyka błędów pamięci oraz kontrola zasobów są ważniejsze niż koszt wejścia i kompilacji. Kod `unsafe` zamknąłbym w małym module-adapterze; reszta API przyjmowałaby bezpieczne typy, zamiast surowych wskaźników. Przy każdym bloku udokumentowałbym niezmienniki: ważność, wyrównanie i długość danych, reguły aliasowania, własność zwalniania, konwencję ABI oraz wymaganą synchronizację.

Ten wybór wymaga audytu granicy FFI i testów na faktycznych platformach. Może być nieopłacalny, gdy dostawca wymaga narzędzi lub ABI niedostępnych w Rustcie, gdy integracja z istniejącym ekosystemem dominuje koszt, albo gdy czas kompilacji nie mieści się w budżecie iteracji. Wtedy porównuję ryzyko, koszt utrzymania i wyniki prototypu zamiast zakładać przewagę któregokolwiek języka.
