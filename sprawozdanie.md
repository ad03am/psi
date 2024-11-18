# Programowanie sieciowe
Autorzy: Adam Czupryński, Szymon Makuch, Michał Sadlej

Data: 18.11.2024r.

##  Komunikacja UDP
Celem zadania było napisanie zestawu dwóch programoów - klienta i serwera wysyłające datagramy UDP.

## Rozwiązanie
Program klienta wysyła kolejne datagramy o przyrastającej wielkości bajtów. Datagramy posiadają ustaloną formę danych: pierwsze dwa bajty datagramu zawierają informację o jego długości, a kolejne bajty powtarzające się litery A-Z. Program serwera weryfikowuje odebrany datagram i odsyła go w odpowiedzi. Następnie klient porównuje wysłany datagram z odebranym aby zweryfikować jego poprawność. Oba programy działają do momentu przerwania połączenia, które następuje w momencie próby wysłania zbyt dużej wiadomości.

Wielkość największego obsługiwanego datagramu wynosi 65507 bajtów. Dla większych datagramów klient zwraca błąd: OSError: [Errno 90] Message too long. Teoretycznie maksymalna wielkość datagramu UDP wynosi 65535 bajtów, jednak faktyczny limit wynika z protokołu IPv4 i wynosi 65507 (65535 bajtów − 8-bajtów nagłówek UDP − 20-bajtów nagłowek IP).
