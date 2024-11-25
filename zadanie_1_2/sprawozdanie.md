# Programowanie sieciowe
Autorzy: Adam Czupryński, Szymon Makuch, Michał Sadlej

Data: 25.11.2024r.

##  Komunikacja UDP
Celem zadania było napisanie zestawu dwóch programoów - klienta i serwera wysyłające datagramy UDP.
Należało zaimplementować prosty protokół niezawodnej transmisji, uwzględniający możliwość gubienia datagramów.

## Rozwiązanie
Program klienta wysyła kolejne datagramy o stałej wielkości bajtów. Datagramy posiadają ustaloną formę danych: pierwszy bajt datagramu zawiera numer sekwencyjny, kolejne dwa bajty zawierają informację o jego długości, a reszta powtarzające się litery A-Z.
```python
def generateDatagram(size: int, seq: int) -> bytes:
    message = bytes([seq, (size & 0xFF00) >> 8, size & 0x00FF])

    for i in range(size - 3):
        message += bytes([ord('A') + (i % 26)])

    return message
```

Program serwera weryfikowuje odebrany datagram i odsyła w odpowiedzi potwierdzenie. Następnie klient odebiera potwierdzenie i przechodzi do następnego datagramu. Oba programy działają do momentu przerwania połączenia, które następuje w momencie próby wysłania zbyt dużej wiadomości.
```python
if checkData(data, seq):
    print("Datagram received correctly")
    s.sendto(b"ACK" + bytes([seq]), address)
    seq = 1 - seq
else:
    print("Error in datagram")
    s.sendto(b"NACK" + bytes([seq]), address)
```

Jeżeli klient nie otrzyma potwierdzenia w ciągu 0.5 sekundy (lub otrzyma negatywne potwierdzenie), ponawia wysłanie datagramu.
```python
s.sendto(message, (host, port))
    try:
        data, _ = s.recvfrom(BUFSIZE)

        if data[:3] == b"ACK" and data[3] == seq:
            print("Acknowledgment received")
            seq = 1 - seq
            break
        else:
            print("Incorrect acknowledgment, retransmitting...")
    except socket.timeout:
        print("Timeout, retransmitting...")
```


## Problemy 

### 1. Nieprawidłowe działanie docker-compose

Program nie działał gdy wywoływaliśmy go poleceniem `docker-compose`, więc wróciliśmy do wywoływania poleceniami `docker build` oraz `docker run`. Wtedy znaleziony został błąd przy przekazywaniu argumentów podczas uruchamiania klienta. Zmiany zostały naniesione do pliku dockerfile i wywołanie poprzez `docker-compose` zaczęło działać.

### 2. Brak numeru sekwencyjnego w wysyłanym datagramie
Na początku nie wysyłaliśmy numeru sekwencyjnego w datagramie, przez co serwer nie miał jak wykryć ominiętego datagramu.
Rozwiązaniem było zawarcie numeru sekwencyjnego w pierwszym bajcie datagramu i porównywanie go z oczekiwanym numerem sekwencyjnym po stronie serwera.

## Opis konfiguracji testowej

Adresy IP serwerów są tworzone automatycznie, klienci odwołują się do nich poprzez hostname. Serwery działają na portach 8000.

Przykład dla serwera pythonowego:
```
"ConfigOnly": false,
        "Containers": {
            "468f5935169703698ec82485d9cf8d4862df43aa85cda304b86ede721b43e5d5": {
                "Name": "z34_p_server",
                "EndpointID": "517be73eff0f5911659a69567bbe70cd0303627c0646f53e6b3a6d02713d39cf",
                "MacAddress": "02:42:ac:15:22:02",
                "IPv4Address": "172.21.34.2/24",
                "IPv6Address": "fd00:1032:ac21:34::2/64"
            }
        },
        "Options": {},
        "Labels": {}
```

## Testy

W celu przetestowania programu sprawdzone zostały wszystkie konfiguracje między sobą. 

Błąd wyrzucany przez klienta pythona:
```
Traceback (most recent call last):
  File "//./client.py", line 49, in <module>
    main(sys.argv[1:])
    ~~~~^^^^^^^^^^^^^^
  File "//./client.py", line 37, in main
    s.sendto(message, (host, port))
    ~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
OSError: [Errno 90] Message too long
```

Błąd wyrzucany przez klienta C:
```
Sending 65507 bytes datagram...
Received 3 bytes from server
Sending 65508 bytes datagram...
send error!
: Message too long
```
