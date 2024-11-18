#!/bin/bash

# Run server commands in a new shell
(
  cd ./C/server
  docker build -t z34_c_server .
  docker run -it --network z34_network --name z34_c_server --network-alias z34_c_server z34_c_server:latest 8000
) &

# Run client commands in a new shell
(
  cd ./C/client
  docker build -t z34_c_client .
  docker run -it --network z34_network --name z34_c_client z34_c_client:latest z34_c_server 8000
) &
