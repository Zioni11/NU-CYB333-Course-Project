From Kalilinux/kali-rolling

Run apt update && apt install -y \
    Nmap \
    Nikto \
    sqlmap \
    python3 \
    python3-pip \
    net-tools \
    iputils-ping 

CMD ["/bin/bash"]