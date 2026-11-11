[← Spis treści](../README.md)
<!-- status: expanded -->

# Wydania, pochodzenie artefaktów i rollback

> Przykłady `rust`: biblioteka standardowa, Edition 2024. API narzędzi i bibliotek zewnętrznych opisano na podstawie źródeł sprawdzonych 11 listopada 2026 r.; szkice `text` wymagają wskazanego środowiska.

## Cele

Po tym rozdziale potrafisz:

- powiązać artefakt ze źródłem i środowiskiem budowania;
- odróżnić hash, podpis i poświadczenie pochodzenia;
- zaprojektować rollback uwzględniający trwałe dane;

## Model — wydaje się artefakt, a nie intencję commitu

Commit wskazuje źródła, ale produkcja uruchamia konkretne binarium. Release powinien połączyć rewizję, lockfile, toolchain, target, flagi, zależności systemowe i wynikowe pliki. Zapisz identyfikator artefaktu, a następnie promuj ten sam plik między środowiskami zamiast ponownie budować „ten sam kod”. Kolejny build może różnić się środowiskiem lub zasobem pobranym podczas kompilacji.

Powtarzalny proces oznacza kontrolowane wejścia i ścieżkę odtworzenia. Bitowa odtwarzalność jest silniejszą własnością: identyczne wejścia dają identyczne bajty. Nie obiecuj jej wyłącznie na podstawie `Cargo.lock`. Timestamps, ścieżki, wersja linkera i zewnętrzne pliki mogą nadal wpływać na wynik. Najpierw porównaj dwa kontrolowane buildy i wyjaśnij różnice.

## Integralność, autentyczność i pochodzenie

Suma kontrolna pomaga wykryć zmianę bajtów względem zaufanej wartości. Nie mówi, kto zbudował plik, jeśli atakujący może zmienić także opublikowany hash. Podpis wiąże treść z kluczem według wybranego systemu zaufania. Pochodzenie (provenance) opisuje proces i wejścia budowania. Lista komponentów oprogramowania (SBOM) pomaga zidentyfikować zależności, lecz sama nie jest raportem ich bezpieczeństwa.

Nie utożsamiaj provenance artefaktu z provenance wskaźnika w modelu pamięci Rusta. Nazwa jest wspólna, ale oznacza inny kontrakt i inny sposób weryfikacji. Procedura instalacji powinna wskazywać, skąd bierze zaufanie do podpisu i jakie zachowanie przy braku lub błędzie weryfikacji jest oczekiwane.

## Kontrakt wersji i changelog

SemVer opisuje kompatybilność publicznego API biblioteki; interfejs CLI, protokół i schemat danych także mogą mieć użytkowników wymagających stabilności. Zmiana kodu wyjścia lub domyślnego formatu wyjścia może złamać skrypty mimo niezmienionych typów Rust. Changelog podaje widoczną zmianę, sposób migracji i ryzyko, a nie listę nazw wewnętrznych funkcji.

Przed publikacją crate'a sprawdź zawartość paczki i wykonaj kontrolę pakowania. Polecenia wymagają konkretnego projektu i nie publikują nic w tym rozdziale:

~~~text
cargo package --list
cargo publish --dry-run --locked
~~~

Zweryfikuj licencję, README, źródła i brak sekretów w paczce. Wynik dry-run nie jest późniejszą publikacją i nie gwarantuje wszystkich uprawnień serwera w chwili wydania. Wersję i kolejność paczek workspace ustal zgodnie z ich zależnościami.

## Rollback jest ograniczony zgodnością danych

Wyobraź sobie nową wersję, która potrafi czytać schemat 2, lecz zaczyna zapisywać schemat 3. Stare binarium rozumie tylko 2. Cofnięcie pliku wykonywalnego nie naprawia już zapisanych danych. Do bezpiecznego powrotu potrzebujesz okna kompatybilności albo jawnej, przetestowanej migracji. Backup bez sprawdzonego odtworzenia nie dowodzi, że możesz wrócić w wymaganym czasie.

~~~rust
#[derive(Debug, PartialEq)]
enum Plan { PowrotMozliwy, WymaganaMigracja }
fn rollback(max_czytany: u32, schemat_danych: u32) -> Plan {
    if schemat_danych <= max_czytany {
        Plan::PowrotMozliwy
    } else {
        Plan::WymaganaMigracja
    }
}
fn main() {
    assert_eq!(rollback(2, 2), Plan::PowrotMozliwy);
    assert_eq!(rollback(2, 3), Plan::WymaganaMigracja);
}
~~~

Model upraszcza zgodność do rosnącego numeru schematu. Rzeczywisty kontrakt musi uwzględnić również znaczenie pól, uprawnienia i skutki uboczne. Warunek `<=` nie jest uniwersalnym algorytmem migracji; pokazuje potrzebę jawnego sprawdzenia zgodności przed operacją.

## Publikowanie wymaga kontrolowanego etapu

Job budujący niezaufaną zmianę nie powinien otrzymywać tokenu publikacji. Oddziel budowanie, weryfikację i udostępnienie artefaktu. Zapisz, kto zatwierdza release, jak blokujesz podmianę pliku po testach i jak identyfikujesz wersję uruchomioną na hoście. Po wdrożeniu wykonaj smoke test prawdziwej ścieżki użytkownika, obserwuj błędy i określ próg przerwania rollout.

## Diagnostyka kompilatora

Błąd pakowania może dotyczyć wykluczonego pliku, niepoprawnych metadanych lub niezgodnego targetu. Otwórz listę zawartości paczki; nie wyciszaj sprawdzania przez ręczne dodanie losowego pliku do builda. Przy różnicy hashy ustal, czy zmieniło się wejście, czy proces jest niedeterministyczny. Nie nazywaj dwóch różnych binariów tym samym artefaktem wyłącznie dlatego, że powstały z tego samego commitu.

## Praktyka produkcyjna

Release ma kryteria wejścia, artefakty, sposób weryfikacji i plan cofnięcia. Przechowuj raport testów, SBOM jeśli wymagany, identyfikatory źródeł i podpisy w kontrolowanym rejestrze. Ćwicz odtwarzanie na reprezentatywnych danych. Rollback może oznaczać wyłączenie funkcji, ograniczenie ruchu albo naprawę do przodu; wybór wynika ze zgodności i aktualnego wpływu, nie z automatycznej wiary w poprzednią wersję.

## Sprawdź, czy rozumiesz

1. Czego hash nie mówi o autorze artefaktu?
2. Dlaczego lockfile nie wystarcza do bitowej odtwarzalności?
3. Co może uniemożliwić powrót do starego binarium?

## Ćwiczenia

- `D10-1` — podstawowe: Wypisz pięć danych pozwalających odtworzyć build. [Rozwiązanie](../rozwiazania/28_ci_cd_i_release_engineering/02_wydania_artefakty_i_rollback.md#d10-1).
- `D10-2` — praktyczne: Ułóż release CLI, którego format JSON ma użytkowników skryptowych. [Rozwiązanie](../rozwiazania/28_ci_cd_i_release_engineering/02_wydania_artefakty_i_rollback.md#d10-2).
- `D10-3` — pogłębione: Zaprojektuj plan cofnięcia wdrożenia zapisującego nowy format danych. [Rozwiązanie](../rozwiazania/28_ci_cd_i_release_engineering/02_wydania_artefakty_i_rollback.md#d10-3).

## Źródła i granice weryfikacji

Pakowanie i dry-run: [Cargo publish](https://doc.rust-lang.org/cargo/commands/cargo-publish.html) i [Cargo package](https://doc.rust-lang.org/cargo/commands/cargo-package.html). Model rollbacku jest przykładem dydaktycznym, nie rzeczywistym migratorem schematów.

## Powiązane tematy

- [Pipeline CI](01_pipeline_ci_msrv_i_targety.md)
- [Incydenty i migracje](../25_debugowanie_i_utrzymanie/02_regresje_migracje_i_incydenty.md)
- [Sekrety i zależności](../27_bezpieczenstwo_aplikacji/02_sekrety_uprawnienia_i_zaleznosci.md)
