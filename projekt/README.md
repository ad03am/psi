# PSI - projekt
Adam Czupryński, Michał Sadlej, Szymon Makuch

Szyfrowany protokół oparty na protokole TCP, tzw. mini TLS. Zaimplementowaliśmy wariant W2 (MAC-then-Encrypt) - w języku Python.

## Struktura
Struktury wiadomości składa się z następujących pól:

### ClientHello
- typ wiadomości
- długość wiadomości
- `g` - generator do algorytmu Diffie-Hellman
- `p` - liczba pierwsza do algorytmu Diffie-Hellman
- `A` - klucz publiczny klienta

### ServerHello
- typ wiadomości
- długość wiadomości
- `B` - klucz publiczny serwera

### Szyfrowana wiadomość
- typ wiadomości
- długość wiadomości
- `iv` - wektor inicjalizacyjny
- zaszyfrowana wiadomość
- MAC

### Szyfrowane EndSession
- typ wiadomości
- długość wiadomości
- powód zakończenia sesji

## Wykorzystane algorytmy 

### Wymiana kluczy
Zastosowaliśmy algorytm wymiany kluczy Diffie-Hellman. Przebieg wymiany:

1. Klient wybiera losową liczbę pierwszą `g` (generator) i liczbę pierwszą `p`
2. Klient generuje prywatny klucz `a`
3. Klient oblicza wartość publiczną: `A = (g^a) mod p`
4. Serwer generuje prywatny klucz `b`
5. Serwer oblicza wartość publiczną: `B = (g^b) mod p`
6. Obie strony wspólnie obliczają klucz symetryczny: `K = (B^a) mod p = (A^b) mod p`

### Szyfrowanie
Zastosowaliśmy prosty algorytm OTP (One-Time Pad):
- Każda wiadomość będzie szyfrowana przy użyciu jednorazowego klucza
- Klucz będzie generowany losowo dla każdej transmisji
- Szyfrowanie polega na operacji XOR między wiadomością a kluczem

Proces generowania klucza dla OTP:
- Initialization vector użyte jest jako pierszy blok
- W pętli generowane są kolejne bloki przy pomocy HMAC-SHA256 poprzez wyliczenie HMAC z poprzedniego bloku używając klucza sesji
- Po przekroczeniu zadanej długości pad jest przycinany do zadanej długości

### Scenariusz przykładowy

#### 1. Inicjacja połączenia i wymiana kluczy
1. Klient generuje liczbę pierwszą `p`, generator `g` i prywatny klucz `a` oraz oblicza `A = g^a mod p`
2. Klient wysyła ClientHello, w którym znajduje się `g`, `p` oraz `A`
3. Serwer generuje prywatny klucz `b` oraz oblicza `B = g^b mod p`
4. Serwer wysyła ServerHello, w którym znajduje się `B`
5. Obie strony obliczają wspólny klucz `K = A^b mod p = B^a mod p`

#### 2. Wysyłanie zaszyfrowanej wiadomości
1. Klient przygotowuje wiadomość `M`
2. Oblicza `MAC = HMAC(M, K)`
3. Łączy wiadomość z MAC: `data = M || MAC`
4. Generuje losowy `IV`
5. Szyfruje `data` używając `K` i `IV`: `encrypted = encrypt(data, K, IV)`
6. Wysyła EncryptedMessage, zawierającą `IV` i `encrypted`

#### 3. Odbieranie zaszyfrowanej wiadomości
1. Serwer odbiera EncryptedMessage
2. Deszyfruje dane używając `K` i `IV`: `decrypted = decrypt(encrypted_data, K, IV)`
3. Rozdziela odszyfrowane dane na wiadomość M i MAC
4. Oblicza własny `MAC' = HMAC(M, K)`
5. Porównuje `MAC'` z otrzymanym `MAC`
6. Jeśli `MAC' = MAC`, wiadomość jest poprawna

#### 4. Zakończenie sesji
Dowolna ze stron może zakończyć sesję wysyłając EndSession

## Realizacja mechanizmu integralności i autentyczności - MAC-then-Encrypt
Mechanizm MAC-then-encrypt ma prostszą implementację i mniejszą złożoność algorytmiczną niż Encrypt-then-MAC, jednocześnie zachowując mechanizmy integralności. Jednocześnie ma nieco niższy poziom bezpieczeństwa, a także wymaga pełnego odszyfrowania przed weryfikacją MAC.

### Przebieg procesu
1. Dla oryginalnej wiadomości generowany jest MAC przez hashowanie przy użyciu wspólnego klucza
2. Oryginalna wiadomość wraz z wygenerowanym MAC jest szyfrowana
3. Weryfikacja i deszyfrowanie po stronie odbiorcy:
   - Odszyfrowanie całej wiadomości (wiadomość + MAC)
   - Ponowne wygenerowanie MAC z odebranej wiadomości
   - Porównanie wygenerowanego MAC z odebranym

## Działanie programu

Przedstawione logi pokazują komunikację sieciową między serwerem a trzema klientami.

### Konfiguracja systemu
* Serwer nasłuchuje na porcie 12345
* Trzej klienci (client1, client2, client3) próbują się połączyć
* Używane są adresy IP w sieci 172.23.0.x
```bash
server-1   | [2025-01-17 19:53:16,312] INFO: Server started on 0.0.0.0:12345
client2-1  | Client server:12345 started
client3-1  | Client server:12345 started
client1-1  | Client server:12345 started
server-1   | Server> help
server-1   | Available commands:
server-1   |   list - List connected clients
server-1   |   disconnect <client_number> - Disconnect a client
server-1   |   help - Show this help
server-1   |   exit - Stop the server
server-1   | Server> list
server-1   | No connected clients
```

### Przebieg komunikacji
* Najpierw wszyscy klienci uruchamiają się
* Client1 łączy się jako pierwszy (z IP 172.23.0.4)
* Następnie łączy się client2 (IP 172.23.0.3)
* Na końcu łączy się client3 (IP 172.23.0.5)
* Każde połączenie inicjuje wymianę kluczy ("Key exchange completed")
```bash
client1-1  | Client> help
client1-1  | Available commands:
client1-1  |   connect - Connect to server
client1-1  |   disconnect - Disconnect from server
client1-1  |   send <message> - Send encrypted message
client1-1  |   help - Show this help
client1-1  |   exit - Exit client
client1-1  | Client> send test
client1-1  | Not connected
client1-1  | Client> connect
server-1   | Server> [2025-01-17 19:54:35,675] INFO: New connection from ('172.23.0.4', 37612)
client1-1  | [2025-01-17 19:54:35,675] INFO: Connected to server:12345
client1-1  | Client> [2025-01-17 19:54:35,675] INFO: Key exchange completed
server-1   | [2025-01-17 19:54:35,675] INFO: Key exchange completed with Client(('172.23.0.4', 37612))
client1-1  | send test
server-1   | [2025-01-17 19:54:39,322] INFO: Message from Client(('172.23.0.4', 37612)): test
client2-1  | Client> connect
server-1   | [2025-01-17 19:54:43,130] INFO: New connection from ('172.23.0.3', 49942)
server-1   | [2025-01-17 19:54:43,131] INFO: Key exchange completed with Client(('172.23.0.3', 49942))
client2-1  | [2025-01-17 19:54:43,131] INFO: Key exchange completed
client2-1  | [2025-01-17 19:54:43,131] INFO: Connected to server:12345
client3-1  | Client> connect
server-1   | [2025-01-17 19:54:47,271] INFO: New connection from ('172.23.0.5', 36938)
server-1   | [2025-01-17 19:54:47,271] INFO: Key exchange completed with Client(('172.23.0.5', 36938))
client3-1  | [2025-01-17 19:54:47,271] INFO: Connected to server:12345
client3-1  | Client> [2025-01-17 19:54:47,271] INFO: Key exchange completed
server-1   | list
server-1   | 1. Client(('172.23.0.4', 37612))
server-1   | 2. Client(('172.23.0.3', 49942))
server-1   | 3. Client(('172.23.0.5', 36938))
```

### Interakcje
* Klienci wysyłają testowe wiadomości
* Client1 rozłącza się samodzielnie
* Server odpina client2 komendą "disconnect"
* Server kończy działanie, co powoduje rozłączenie client3
```bash
client2-1  | Client> send client two
server-1   | Server> [2025-01-17 19:54:55,962] INFO: Message from Client(('172.23.0.3', 49942)): client two
client3-1  | send client three
server-1   | [2025-01-17 19:55:02,970] INFO: Message from Client(('172.23.0.5', 36938)): client three
client1-1  | Client> disconnect
server-1   | [2025-01-17 19:55:07,636] INFO: Received EndSession from Client(('172.23.0.4', 37612)): Client initiated disconnect
server-1   | [2025-01-17 19:55:07,637] INFO: Disconnecting Client(('172.23.0.4', 37612))
client1-1  | [2025-01-17 19:55:07,637] ERROR: Connection closed by server
client1-1  | [2025-01-17 19:55:07,637] WARNING: Not connected
client1-1  | client receive loop ended
client1-1  | [2025-01-17 19:55:07,637] INFO: Client disconnected
server-1   | list
server-1   | 1. Client(('172.23.0.3', 49942))
server-1   | 2. Client(('172.23.0.5', 36938))
server-1   | Server> disconnect 1
server-1   | [2025-01-17 19:55:15,334] INFO: Disconnecting Client(('172.23.0.3', 49942))
client2-1  | Client> Received message: Server initiated disconnect
client2-1  | [2025-01-17 19:55:15,653] ERROR: Connection closed by server
client2-1  | [2025-01-17 19:55:15,654] INFO: Client disconnected
client2-1  | client receive loop ended
server-1   | Server> exit
server-1   | [2025-01-17 19:56:14,771] INFO: Disconnecting Client(('172.23.0.5', 36938))
client3-1  | Client> [2025-01-17 19:56:14,771] ERROR: Connection closed by server
client3-1  | [2025-01-17 19:56:14,772] INFO: Client disconnected
client3-1  | client receive loop ended
server-1 exited with code 0
```

### Wireshark
Poniższy zrzut ekranu pokazuje:
* Komunikację TCP między adresami 172.23.0.x
* Pakiety ARP służące do rozpoznawania adresów
* Wymianę pakietów SYN podczas nawiązywania połączeń
* Pakiety PSH+ACK przy przesyłaniu danych
* Różne długości pakietów wskazujące na szyfrowaną komunikację

![Screen z Wiresharka](wireshark.png)
