FROM ubuntu:latest

RUN export DISPLAY=:0.0
RUN apt-get update
RUN apt-get install kubuntu-desktop
RUN adduser -D server
WORKDIR /home/server
USER server

COPY . .
RUN bash setup.sh

ENTRYPOINT [ "python3", "TwitchPlays.py" ]