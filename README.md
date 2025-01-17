# PSI 24Z
Repozytorium zawiera rozwiązania do zadań z przedmiotu Programowanie Sieciowe

## Zadanie 1.1
W folderze zadanie_1_1 znajduje się rozwiązanie do zadania 1.1. Jest ono podzielone na kod napisany w `C` oraz w `Pythonie`. W obu językach zostały zaimplementowane serwery oraz klienci. Programy działają międzyplatformowo,
tj. przykładowo klient w `Pythonie` może połączyć się nie tylko z serwerem w `Pythonie` ale również z serwerem w `C`. 
W pliku run.sh zostało zaimplementowane przykładowe użycie.

## Zadanie 1.2
W folderze zadanie_1_2 znajduje się rozwiązanie do zadania 1.2. Jest ono podzielone na klienta i serwer. Program uruchamiany jest poprzez polecenia `docker-compose build` a następnie `docker-compose up`. W celu zasymulowania prawdziwych warunków w sieci, na drugim terminalu należy uruchomić polecenie `docker exec z34_client tc qdisc add dev eth0 root netem delay 1000ms 500ms loss 50%`. 

## Zadanie 2
W folderze zadanie_2 znajduje się rozwiązanie do zadania 2. Jest ono podzielone na klienta i serwer. Program uruchamiany jest poprzez polecenia `docker-compose build` a następnie `docker-compose up`.

## Projekt
W folderze projekt znajduje się rozwiązanie do projektu. W celu uruchomienia proejktu należy wywołać polecenie `docker compose up --build`. Następnie w osobnym terminalu należy wywołać polecenie `docker attach [nazwa_kontenera]` aby uzyskać dostęp do klienta. Po uruchomieniu klienta można wywołać polecenie `help` aby zobaczyć dostępne opcje.
