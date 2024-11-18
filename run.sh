#!/bin/bash

echo ==============================
echo C server - Python client combo
echo ==============================

(
  cd ./C/server
  docker build -t z34_c_server .
  docker run --network z34_network --name z34_c_server --network-alias z34_c_server --hostname z34_c_server z34_c_server:latest 8000
) &

sleep 2

(
    cd ./Python/client
    docker build -t z34_p_client .
    docker run --network z34_network --name z34_p_client z34_p_client z34_p_server 8000
) &

sleep 7

docker logs -f z34_c_server &
docker logs -f z34_p_client &

sleep 3

docker rm -f z34_c_server z34_p_client 2>/dev/null || true

sleep 3

echo ==============================
echo Python server - C client combo
echo ==============================

(
    cd ./Python/server
    docker build -t z34_p_server .
    docker run --network z34_network --name z34_p_server --hostname z34_p_server z34_p_server   
) &

sleep 2

(
  cd ./C/client
  docker build -t z34_c_client .
  docker run --network z34_network --name z34_c_client z34_c_client:latest z34_c_server 8000
) &

sleep 7

docker logs -f z34_p_server &
docker logs -f z34_c_client &

sleep 3

docker rm -f z34_p_server z34_c_client 2>/dev/null || true
