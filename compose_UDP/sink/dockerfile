FROM gcc:4.9
COPY . /Server
WORKDIR /Server/
RUN gcc -o udp_sink2 udp_sink2.c
EXPOSE 8888
CMD ["./udp_sink2", "8888"]
