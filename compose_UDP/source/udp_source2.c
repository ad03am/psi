#include "./udp_source_sink.h"
#include <arpa/inet.h>
#include <err.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>

#define bailout(s) {perror(s); exit(1); }
#define Usage() { errx( 0, "Usage: %s <host> <port>\n", argv[0]); }
#define timeinms(tv) ( (tv.tv_sec) * 1000.0 + (tv.tv_usec) / 1000.0 )

#define TEST_MAX_SIZE 70000

void prepare_dgram(char *databuf, int length) {
    databuf[0] = (length >> 8) & 0xFF;
    databuf[1] = length & 0xFF;
    int i = 2;

    int reported_length = ((databuf[0] << 8) | databuf[1]) & 0xFFFF;
    for (i; i < length; i++) {
        databuf[i] = 'A' + ((i - 2) % 26);
    }
}

int main(int argc, char *argv[])
{
    int sock;
    struct sockaddr_in server;
    struct hostent *hp;
    char databuf[TEST_MAX_SIZE];
    char recvbuf[1024];
    int dgram_size = 65500;
    socklen_t addr_len = sizeof(server);


    if ( argc !=3) {
        Usage();
    }

    /* Create socket. */
    sock = socket( AF_INET, SOCK_DGRAM, 0 );
    if (sock == -1)
        bailout("opening stream socket");

    /* uzyskajmy adres IP z nazwy . */
    server.sin_family = AF_INET;
    hp = gethostbyname2(argv[1], AF_INET );

    /* hostbyname zwraca strukture zawierajaca adres danego hosta */
    if (hp == (struct hostent *) 0) {
        errx(2, "%s: unknown host\n", argv[1]);
    }
    printf("address resolved...\n");

    memcpy((char *) &server.sin_addr, (char *) hp->h_addr, hp->h_length);
    server.sin_port = htons(atoi( argv[2]) );

    connect (sock, (struct sockaddr *) &server, sizeof(server) );
    printf("sending the alphabet...\n");

    while (dgram_size <= TEST_MAX_SIZE) {
        ssize_t nread;
        prepare_dgram(databuf, dgram_size);

        printf("Sending %d bytes datagram...\n", dgram_size);
        if ((send( sock, databuf, dgram_size, 0 )) <0 ) {
            perror("send error!\n");
            break;
	    }

        nread = recvfrom(sock, recvbuf, sizeof(recvbuf), 0, (struct sockaddr *) &server, &addr_len);
        if (nread < 0 ) {
	        fprintf(stderr, "failed recvfrom\n");
            continue;               /* Ignore failed request */
	    }
        else {
            printf("Received %d bytes from server\n", nread);
        }

        dgram_size += 1;
	}

    printf("End this...\n");
    close(sock);
    exit(0);
}
