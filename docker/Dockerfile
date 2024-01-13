FROM debian:bookworm-slim

WORKDIR /root

RUN apt-get update && apt-get install --no-install-recommends -y openssh-server python3 sudo

RUN adduser pi && usermod -aG sudo pi

COPY 010_pi-nopasswd /etc/sudoers.d/
COPY extra_ssh.conf /etc/ssh/sshd_config.d/

USER pi
RUN mkdir -p /home/pi/.ssh
COPY id_rsa.pub /home/pi/.ssh/
RUN cat /home/pi/.ssh/id_rsa.pub >> /home/pi/.ssh/authorized_keys

USER root
COPY start.sh ./
RUN chmod u+x ./start.sh


CMD ["sh", "-c", "/root/start.sh"]
