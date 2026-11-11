# Niezależny przegląd: język, pamięć i granice systemu, działy 01–23

Data: 2026-11-11. Przegląd źródeł i rozwiązań bez zmieniania treści kompendium lub Git. Jedynym dodanym plikiem jest ten raport. Podstawa wymagań: `docs/superpowers/plans/2026-11-11-poglebienie-30-dzialow.md`, `CONTRIBUTING.md` oraz dyspozycja pogłębienia pełnych 30 działów, z zachowaniem wartościowej wcześniejszej treści.

## Zakres i sposób oceny

Odkryto ścieżki przez `rg --files`. Przejrzano inwentarz i nagłówki wszystkich 81 rozdziałów oraz 23 map w działach 01–23. Wszystkie te działy zawierają rozdziały, a wszystkie 81 rozdziałów ma status `expanded`. Jest to kontrola zakresu i struktury; sam znacznik nie dowodzi jakości opracowania.

W całości, łącznie z przykładami, pytaniami, ćwiczeniami i odpowiadającymi im rozwiązaniami, przeczytano 32 rozdziały:

| Dział | Rozdziały przeczytane w całości |
|---|---|
| 03 | 03_referencje_i_borrowing; 05_lifetimes |
| 05 | 04_variance_subtyping_i_dropck; 05_hrtb_gat_rpit_i_impl_trait; 06_dyn_compatibility_vtables_i_dispatch |
| 06 | 04_closures_i_fn_traits; 05_iteratory |
| 08 | 03_zaleznosci_features_i_cfg |
| 10 | 03_arc_mutex_rwlock_i_condvar; 04_send_sync_i_atomiki; 05_atomics_i_memory_ordering; 06_lock_free_i_aba |
| 11 | 02_executor_waker_i_poll; 04_anulowanie_timeouty_i_blocking; 05_pin_unpin_i_self_referential |
| 13 | 01_pliki_io_i_procesy; 02_siec_i_protokoly |
| 15 | 01_komendy_argumenty_i_konfiguracja; 02_strumienie_sygnaly_testy_i_dystrybucja |
| 16 | 01_http_routing_stan_i_bledy; 02_middleware_limity_testy_i_shutdown |
| 17 | 01_repozytoria_pule_i_transakcje; 02_migracje_testy_i_odtwarzanie |
| 19 | 01_borrow_checker_polonius_i_model_pamieci |
| 20 | 04_const_eval_simd_i_asm |
| 21 | 01_unsafe_i_soundness; 02_raw_pointers_aliasing_i_provenance; 03_layout_alignment_i_uninitialized_memory |
| 22 | 01_ffi_abi_i_repr; 02_ffi_safe_wrappers_i_ub |
| 23 | 01_wasm_no_std_i_embedded; 02_no_std_allocatory_i_embedded |

Tabela obejmuje całą zleconą próbkę wysokiego ryzyka oraz dodatkowe lektury dotyczące auto traits, ABA, dyn compatibility, async closures, cech Cargo, sieci, CLI, web, migracji i granic no_std. Pozostałych 49 rozdziałów nie oceniono linia po linii. Dla nich nie należy interpretować braku uwag jako potwierdzenia poprawności całej treści.

Porównano również strukturę i dłuższe usunięte fragmenty ze źródłem w `/Users/sebastianlarma/Documents/Codex/Rust_compendium`. Wszystkie 72 wcześniejsze rozdziały z badanego zakresu nadal istnieją. W sprawdzonej próbce zachowano dawne modele i przykłady, a korekty Pin/FFI oraz nowe wyjaśnienia mają uzasadnienie merytoryczne. Nie znaleziono utraty wartościowego większego opracowania; kontrola nie jest pełnym ręcznym porównaniem każdego zdania całego repozytorium.

Nie ponawiano pełnego verify ani wszystkich doctestów. Przekazany wynik 597 testów traktowano jako informację o wcześniejszej weryfikacji, a nie argument za soundness lub poprawnością protokołów. Przegląd oceniał kontrakt i możliwe przeploty także tam, gdzie typy i testy mogą pozostać poprawne.

## Critical

Brak potwierdzonych uwag tej kategorii w przeczytanej próbce.

## Important

### I1. Migracja z dual-write nie zabezpiecza zapisu przez poprzednią wersję — ZAMKNIĘTA

Status po wąskiej kontroli poprawki 2026-11-11: **zamknięta**. Poniższy opis zachowuje pierwotne ustalenie i lokalizacje sprzed poprawki; aktualny kontrakt oraz uzasadnienie zamknięcia opisano dalej.

Miejsce: `17_bazy_danych_i_persystencja/02_migracje_testy_i_odtwarzanie.md:20`, w kontekście deklarowanego rolling deployment z linii 16–18 i backfillu z linii 26–28. Ten sam brak powtarza `rozwiazania/17_bazy_danych_i_persystencja/02_migracje_testy_i_odtwarzanie.md:7`.

Nowy kod ma zapisywać obie kolumny i preferować nową przy odczycie, a backfill aktualizuje tylko wartości NULL. Nie zapisano jednak warunku, że przed takim odczytem i backfillem **wszyscy** writerzy muszą już utrzymywać obie reprezentacje, ani mechanizmu synchronizacji dla starych writerów. Rozdział wprost dopuszcza współistnienie starej i nowej aplikacji; wycofanie starych klientów pojawia się dopiero przy zawężaniu schematu.

Kontrprzykład nie wymaga nawet równoczesnych transakcji:

1. Wiersz ma `pelna_nazwa='A'`, `nazwa_wyswietlana=NULL`.
2. Backfill zapisuje nową nazwę jako `'A'`.
3. Stara aplikacja zapisuje wyłącznie `pelna_nazwa='B'` i zatwierdza.
4. Nowa aplikacja preferuje nie-NULL `nazwa_wyswietlana` i nadal zwraca `'A'`.
5. Powtórzenie backfillu z `IS NULL` pomija ten wiersz.

Wynik jest nieaktualny i może zostać utrwalony po usunięciu starej kolumny. `NOT NULL`, kompletność backfillu i transakcja obejmująca dwa zapisy nowego kodu nie wykrywają tego przypadku. To luka w zalecanym protokole zgodności, nie problem kosmetyczny ani brak testu kompilacji.

Poprawka: rozdziel wdrożenie na wyraźne fazy. Najpierw dodaj kolumnę i wdroż wersję zgodności, która nadal czyta starą reprezentację, ale utrzymuje dual-write. Poczekaj na aktualizację wszystkich writerów, w tym workerów, narzędzi i dopuszczalnych wersji rollbacku. Dopiero wtedy rozpocznij backfill oraz przełączenie odczytu. Alternatywnie zapewnij synchronizację w bazie dla zapisów starego klienta, np. właściwie zaprojektowany trigger, z jednoznaczną regułą źródła prawdy. Uzupełnij rozwiązanie C06-1 i test zgodności o zapis starej wersji po przetworzeniu danego wiersza przez backfill.

Wniosek o błędzie wynika z pokazanej sekwencji zapisów. Dokumentacja PostgreSQL potwierdza odrębną ocenę warunków UPDATE i możliwość synchronizacji zmian triggerem wykonywanym w transakcji polecenia; sama izolacja nie dopisuje pominiętej aktualizacji drugiej kolumny. Źródła sprawdzone podczas przeglądu: [PostgreSQL: transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html), [PostgreSQL: trigger behavior](https://www.postgresql.org/docs/current/trigger-definition.html).

#### Kontrola zamknięcia I1

Ponownie przeczytano wyłącznie poprawioną sekwencję migracji, scenariusz regresji oraz rozwiązanie C06-1. Nie otwierano nowego szerokiego przeglądu ani nie powtarzano testów.

- `17_bazy_danych_i_persystencja/02_migracje_testy_i_odtwarzanie.md:18` ustanawia barierę wszystkich writerów, obejmuje zakończenie wcześniejszych transakcji i zabrania powrotu starego writera przez rollback. Wersja zgodności nadal czyta stare pole.
- Linia 20 zachowuje starą kolumnę jako źródło prawdy aż do uzgodnienia danych. Przypisanie w SQL korzysta z bieżącej wartości, a atomowy dual-write według jednej transformacji podtrzymuje zgodność podczas backfillu.
- Linia 30 używa `IS DISTINCT FROM`, więc naprawia również nie-NULL rozbieżności pozostawione przez starą wersję, zamiast ograniczać się do brakujących wartości. Linie 31–33 przesuwają odczyt nowego pola za kontrolę zgodności.
- Linie 36 i 38 zawierają kontrprzykład `Ala → przedwczesny backfill → stary zapis Beata`, stan wymagający naprawy `(Beata, Ala)` oraz oba porządki backfillu i poprawnego dual-write. Pozwala to odróżnić naprawiony protokół od wcześniejszego, nawet bez argumentu o poprawnej kompilacji.
- `rozwiazania/17_bazy_danych_i_persystencja/02_migracje_testy_i_odtwarzanie.md:7`, 9 i 11 stosują tę samą kolejność dla C06-1: zgodność wszystkich writerów, uzgodnienie także istniejących wartości, przełączenie odczytu i dopiero późniejsze usunięcie starej reprezentacji.

Poprawka zamyka wskazany kontrprzykład oraz jego przyczynę. Nie pozostaje otwarta uwaga Important z tego przeglądu. Ocena dotyczy spójności opisanego protokołu; nie oznacza wykonania testu integracyjnego PostgreSQL, którego brak jest jawnie zaznaczony w treści. Przekazanego wyniku siedmiu doctestów nie użyto jako dowodu poprawności migracji.

## Minor

Brak dodatkowych potwierdzonych wad wymagających osobnej poprawki. Nie podniesiono skondensowanego formatowania części rozwiązań do rangi błędu merytorycznego.

## Kontrole źródeł i świadomie odrzucone zarzuty

- Nowsze API w rozdziale 20/04 nie są zmyślone ani błędnie oznaczone jako lokalnie przetestowane. Aktualna dokumentacja potwierdza stabilizację `NumBuffer` i `algebraic_*` w Rust 1.98. Opis prawidłowo rozdziela kontrakt dokumentacyjny od testu na 1.90 oraz informuje o słabszej powtarzalności operacji algebraicznych. Sprawdzono [NumBuffer](https://doc.rust-lang.org/std/fmt/struct.NumBuffer.html) i [f32: algebraic operators](https://doc.rust-lang.org/std/primitive.f32.html#algebraic-operators).
- Pinning, możliwość `Pin::set`, projekcja, strukturalnie przypięte pola i ograniczenia Drop przedstawiono w zgodzie z [dokumentacją std::pin](https://doc.rust-lang.org/std/pin/index.html). Nie zgłoszono dozwolonego przeniesienia uchwytu jako przeniesienia pointee.
- Przykład podziału slice uwzględnia granice, pusty slice i ZST; nie zgłoszono pokrywania adresów ZST jako automatycznego naruszenia rozłączności elementów. Kontrakt porównano z [from_raw_parts_mut](https://doc.rust-lang.org/std/slice/fn.from_raw_parts_mut.html).
- `AsyncFn` jest stabilne od 1.85, podczas gdy bezpośrednia metoda `async_call` pozostaje osobną niestabilną powierzchnią. Opis tej różnicy jest prawidłowy: [AsyncFn](https://doc.rust-lang.org/std/ops/trait.AsyncFn.html).
- TAIT nadal opisano jako nightly zgodnie z [Unstable Book](https://doc.rust-lang.org/unstable-book/language-features/type-alias-impl-trait.html). Status Poloniusa jest zgodny z przywołanym [oficjalnym statusem projektu](https://rust-lang.github.io/polonius/current_status.html); raport nie wyprowadza z tej strony prognozy stabilizacji.
- Brak zwykłego `abort` dla rozpoczętego `spawn_blocking` jest prawidłową granicą opisaną przez [Tokio](https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html). Nie uznano timeoutu lub upuszczenia future za rollback efektu zewnętrznego.
- Obsługa SQLx przez `&mut *tx`, konsumujące `commit(self)` i awaryjny rollback są zgodne z [Transaction 0.8.6](https://docs.rs/sqlx/0.8.6/sqlx/struct.Transaction.html). Nie wymagano działającego serwera w zwykłym docteście przykładu jawnie oznaczonego jako szkic.
- Kontrakt `GlobalAlloc` rozdziela zerowy Layout i niedozwolone zerowe żądanie alloc, brak unwind oraz niepewność liczby rzeczywistych alokacji. Potwierdza to [GlobalAlloc](https://doc.rust-lang.org/std/alloc/trait.GlobalAlloc.html).

Braku uruchomienia integracji axum/SQLx, targetu embedded, DMA, asm, nightly SIMD ani kodu wymagającego Rust 1.98 nie traktowano samodzielnie jako wady, ponieważ ograniczenia są jawne i plan dopuszcza takie bloki `text`. Nie jest to jednak potwierdzenie wykonania tych integracji. Nie przeprowadzono Miri, sanitizera, modelowania Loom, testu sprzętu ani dowodu formalnego każdego unsafe API. Działów 24–30 i materiałów przekrojowych ten raport nie obejmuje.

## Werdykt zakresu i jakości

Zakres strukturalny działów 01–23 jest wykonany: nie pozostawiono samych map, zachowano wcześniejsze ścieżki i dołożono opracowania do wcześniej pustych działów. W przeczytanej próbce rozbudowa jest rzeczywista: objaśnia pochodzenie i ważność danych, granice API, koszty, stany pośrednie, kontrprzykłady i decyzje produkcyjne. Szczególnie dobrze rozdziela typowanie od soundness, data race od błędu protokołu, flush od trwałości oraz timeout od nieznanego wyniku operacji.

Próbka nie daje podstaw do pełnej akceptacji merytorycznej wszystkich 81 rozdziałów. **Po wąskiej kontroli poprawki I1 jest zamknięta; w zbadanej próbce nie pozostają otwarte uwagi Critical ani Important.** Poprawiony rozdział migracji i rozwiązanie C06-1 akceptuję w zakresie zgłoszonego problemu. Ograniczenia pierwotnej próbki i brak wykonania opisanych integracji pozostają aktualne; kontrola zamknięcia nie rozszerza zakresu audytu.
