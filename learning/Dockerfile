FROM golang:1.21

RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends openssh-server \
    && echo "root:Docker!" | chpasswd
COPY sshd_config /etc/ssh/

WORKDIR /app
COPY api ${WORKDIR}
RUN go mod download && go mod verify
RUN go build -v -o /usr/local/bin/app main.go

CMD service ssh start && app