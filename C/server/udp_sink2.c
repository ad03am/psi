#include <err.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

#define BUF_SIZE 70000

#define bailout(s) { perror( s ); exit(1);  }
#define Usage() { errx( 0, "Usage: %s [port]\n", argv[0]); }
#define timeinms(tv) ( (tv.tv_sec) * 1000.0 + (tv.tv_usec) / 1000.0 )

int validate_datagram(const char *buf, int length) {
    unsigned int reported_length = ((buf[0] << 8) | buf[1]) & 0xFFFF;
    int i = 2;
    if (reported_length != length) {
        fprintf(stderr, "Length mismatch: reported %d, actual %d\n", reported_length, length);
        return 0;
    }

    for (i; i < length; i++) {
        if (buf[i] != 'A' + ((i-2) % 26)) {
            fprintf(stderr, "Content mismatch at byte %d: %d vs %d\n", i, buf[i], 'A' + ((i-2) % 26));
            return 0;
        }
    }
    return 1;
}

int main(int argc, char *argv[]) {
    int                      sfd, s;
    char                     buf[BUF_SIZE], reply[] = "OK";
    ssize_t                  nread;
    struct sockaddr_in       server, client;
    socklen_t                client_len = sizeof(client);

    if (argc != 2) 
        Usage();

    if ( (sfd=socket(AF_INET, SOCK_DGRAM, 0)) < 0)
	bailout("socker() ");

   server.sin_family      = AF_INET;  /* Server is in Internet Domain */
   server.sin_port        = htons(atoi(argv[1]));         /* Use any available port      */
   server.sin_addr.s_addr = INADDR_ANY; /* Server's Internet Address   */

   if ( (s=bind(sfd, (struct sockaddr *)&server, sizeof(server))) < 0)
      bailout("bind() ");
   printf("bind() successful\n");
   printf("sfd: %d \n", sfd);

    /* Read datagrams and echo them back to sender. */
   printf("waiting for alphabet...\n");

    for (;;) {
        nread = recvfrom(sfd, buf, BUF_SIZE, 0, (struct sockaddr *) &client, &client_len);
        if (nread <0 ) {
            fprintf(stderr, "failed recvfrom\n");
            continue;               /* Ignore failed request */
        }
        printf("Received %d bytes datagram\n", nread);

        if (validate_datagram(buf, nread)) {
            sendto(sfd, reply, sizeof(reply), 0, (struct sockaddr *)&client, client_len);
            printf("Datagram validated, response sent.\n");
        } else {
            fprintf(stderr, "Invalid datagram\n");
            sendto(sfd, reply, sizeof(reply), 0, (struct sockaddr *)&client, client_len);
            continue;
        }
    }

    printf("Close sink...\n");
    close(sfd);
    exit(0);
}
