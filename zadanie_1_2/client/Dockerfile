FROM python:3
ADD client.py /
RUN apt-get update
RUN apt-get install -y iproute2
ENTRYPOINT [ "python3", "./client.py", "z34_server"]
