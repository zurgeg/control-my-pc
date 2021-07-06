FROM ubuntu:latest

RUN apt-get update
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && \
RUN env DEBIAN_FRONTEND=noninteractive apt-get install -y kubuntu-desktop
RUN adduser -D server
WORKDIR /home/server
USER server

COPY . .
RUN bash setup.sh

ENTRYPOINT [ "python3", "TwitchPlays.py" ]