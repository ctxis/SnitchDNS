#!/bin/bash

systemctl start snitchdns.service
systemctl start apache2

./venv.sh flask snitch_start

iptables -t nat -I PREROUTING --src 0/0 -p tcp --dport 53 -j REDIRECT --to-ports 2024
iptables -t nat -I PREROUTING --src 0/0 -p udp --dport 53 -j REDIRECT --to-ports 2024

/bin/bash