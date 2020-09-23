# docker build --rm -t mcast-app:latest .

FROM ubuntu:18.04
LABEL maintainer="Jacob Miller (jake_son@yahoo.com)"

WORKDIR /root/app/
COPY mcast.py mcast.py

RUN apt-get update && apt-get install -y -q \
    python3.7

ENV PATH="${PATH}:/usr/bin/"
