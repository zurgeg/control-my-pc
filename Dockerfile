FROM ubuntu:latest

RUN apt-get update
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
RUN env DEBIAN_FRONTEND=noninteractive apt-get install -y kubuntu-desktop
RUN adduser --disabled-password server
WORKDIR /home/server
USER server

COPY . .
RUN apt-get -y install python3-pip
RUN bash setup.sh

ENTRYPOINT [ "source", "start.sh" ]