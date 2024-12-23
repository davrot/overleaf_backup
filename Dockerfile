FROM ubuntu:24.04

# Ensure non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Update and install packages
RUN apt update 
RUN apt -y install mc 
RUN apt -y install bash
RUN apt -y install openssh-server
RUN apt -y install python3-pip
RUN apt -y install python3-argh
RUN apt -y install git-all
# RUN apt -y install golang-go
RUN apt -y install curl
RUN apt -y install openssl
RUN apt -y install libpam-script
RUN apt -y install sudo
RUN apt -y install rush
RUN apt -y install inetutils-syslogd
RUN apt -y install python3-docker

# RUN mkdir -p /compile && cd /compile && git clone https://github.com/kha7iq/kc-ssh-pam.git && cd /compile/kc-ssh-pam && go build && mkdir -p /etc/kc-ssh-pam && cp /compile/kc-ssh-pam/kc-ssh-pam /etc/kc-ssh-pam 

RUN cp -a /etc /etc_original
RUN rm -f /etc_original/hostname
RUN rm -f /etc_original/hosts
RUN rm -f /etc_original/resolv.conf

# Copy initialization script
COPY files/init.sh /init.sh
RUN chmod +x /init.sh

# Expose SSH port
EXPOSE 22

ENTRYPOINT ["/init.sh"]




