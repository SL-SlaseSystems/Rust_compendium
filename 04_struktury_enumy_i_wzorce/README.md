[← Spis treści](../README.md)

# 4. Struktury, enumy i wzorce

## Dla kogo i po co

Dla osób chcących modelować domenę tak, aby niepoprawne stany były trudne albo niemożliwe do utworzenia.

## Wymagania wstępne

Ownership, referencje, funkcje i podstawowe typy.

## Kolejność materiałów

1. [Struktury, enumy i metody](01_struktury_enumy_i_metody.md)
2. [Wzorce i `match`](02_wzorce_i_match.md)

## Po tym dziale

Umiesz budować typy domenowe, wiązać zachowanie z danymi i wyczerpująco obsługiwać warianty.

## Jak pracować z działem

Zacznij od reprezentacji stanów: struktura przechowuje wszystkie pola, a enum jeden wariant. Następnie sprawdź, czy klient może ominąć walidację przez publiczne pole. Przy wzorcach zawsze zapisz, czy dopasowujesz wartość, `&T`, czy `&mut T`; od tego zależą przeniesienia i referencje wiązane w ramionach.

Ćwiczenia `A16` i `A17` obejmują trzy poziomy trudności. Prowadzą od metod newtype do skalowania bez częściowej mutacji i parsera ramki o sprawdzanej długości. Rozwiązania są pełnymi przykładami z przypadkami brzegowymi, a nie jedynie wskazówkami. Zachowują rozróżnienie między błędnym kształtem danych a poprawną pustą zawartością.

## Punkt kontrolny

Zastąp dwie wykluczające się flagi enumem i opisz wszystkie przejścia wyczerpującym `match`. Wyjaśnij, co zmieni dodanie wariantu, a co ukryje ramię `_`. Umiesz także dopasować pożyczony `String` bez przejęcia bufora i odróżnić guard od wzorca.

Dalej przejdź do generyków i traitów: tam te same kontrakty będą opisywane dla wielu typów. Własny model danych powinien już wykluczać nielegalne kombinacje, zanim zaczniesz uogólniać implementację.

## Co dalej

Przejdź do traits i generics, aby abstrahować zachowanie bez rozmywania modelu domenowego.

Następny dział: [Generics, traits i system typów](../05_generics_traits_i_system_typow/README.md).
