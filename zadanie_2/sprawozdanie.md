# Programowanie sieciowe
Autorzy: Adam Czupryński, Szymon Makuch, Michał Sadlej

Data: 02.12.2024r.

##  Komunikacja TCP
Celem zadania było napisanie zestawu dwóch programów - klienta i serwera komunikujących się poprzez TCP. Każdy klient łączący się z serwerem miał być obsługiwany na osobnym wątku.

## Rozwiązanie
Program klienta wysyła 100kB na serwer:
```python
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    s.sendall(data_to_send)

    print(f"Sent {len(data_to_send)} bytes")
```

W kodzie serwera znajduje się kod wątku wywoływanego podczas akceptowania klienta:
```python
def do_client(conn, addr) -> None:
    with conn:
        print("Connected by client at", addr)
        received_data = b''
        while len(received_data) < DATA_SIZE:
            data = conn.recv(BUFSIZE)
            if not data:
                break
            received_data += data
        print(f"Received {len(received_data)} bytes")
        conn.sendall(received_data)
        print("Data sent back to client")

    conn.close()
    print("Connection closed by client at", addr)
```

Program serwera nasłuchuje na swoim porcie i akceptuje przychodzących klientów oddelegowując ich na powstający wówczas wątek:
```python
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(5)

    while True:
        conn, addr = s.accept()

        client = threading.Thread(target=do_client, args=(conn, addr))
        client.start()
```

## Problemy 

Żadnych problemów.

## Opis konfiguracji testowej

Adresy IP serwerów są tworzone automatycznie, klienci odwołują się do nich poprzez hostname. Serwery działają na portach 8000.

```
"Containers": {
            "f5d1f400aad57caa698254e03643f0e594852da863ec94448810473cc95fd0f5": {
                "Name": "z34_server2",
                "EndpointID": "566418a20b775706ab7ef15f417d4ae8bd3b72ea67afddeef48dc363134d65ec",
                "MacAddress": "02:42:ac:15:22:02",
                "IPv4Address": "172.21.34.2/24",
                "IPv6Address": "fd00:1032:ac21:34::2/64"
            }
        },
```

## Testy

W celu przetestowania konfiguracji, z jednym serwerem połączyło się jednocześnie dwóch klientów.
To ich output:

### Serwer
```python
Server at 0.0.0.0:8000
Connected by client at ('172.21.34.3', 48686)
Received 102400 bytes
Data sent back to client
Connection closed by client at ('172.21.34.3', 48686)
Connected by client at ('172.21.34.4', 34488)
Received 102400 bytes
Data sent back to client
Connection closed by client at ('172.21.34.4', 34488)
Connected by client at ('172.21.34.3', 44302)
Received 102400 bytes
Data sent back to client
Connection closed by client at ('172.21.34.3', 44302)
```

### Klient 1 
```python
smakuch@bigubu:~/psi/zadanie_2/client$ docker run -it --network z34_network z34_client 
Connecting to z34_server2:8000
Sent 102400 bytes
Received 102400 bytes
Client finished.
smakuch@bigubu:~/psi/zadanie_2/client$ docker run -it --network z34_network z34_client 
Connecting to z34_server2:8000
Sent 102400 bytes
Received 102400 bytes
Client finished.
```


### Klient 2
```python
smakuch@bigubu:~/psi/zadanie_2/client$ docker run -it --network z34_network z34_client
Connecting to z34_server2:8000
Sent 102400 bytes
Received 102400 bytes
Client finished.
```
