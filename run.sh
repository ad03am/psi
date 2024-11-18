#!/bin/bash

(
  cd ./C/server
  docker build -t z34_c_server .
  docker run --network z34_network --name z34_c_server --network-alias z34_c_server z34_c_server:latest 8000
) &

(
  cd ./C/client
  docker build -t z34_c_client .
  docker run --network z34_network --name z34_c_client z34_c_client:latest z34_c_server 8000
) &

sleep 5

docker logs -f z34_c_server &
docker logs -f z34_c_client &

docker rm -f z34_c_server z34_c_client z34_p_server z34_p_client 2>/dev/null || true

wait 1

(
    cd ./Python/server
    docker build -t z34_p_server .
    docker run --network z34_network --name z34_p_server --hostname z34_p_server z34_p_server   
) &

(
    cd ./Python/client
    docker build -t z34_p_client .
    docker run --network z34_network --name z34_p_client z34_p_client z34_p_server 8000
) &

sleep 5

docker logs -f z34_c_server &
docker logs -f z34_c_client &

docker rm -f z34_c_server z34_c_client z34_p_server z34_p_client 2>/dev/null || true
