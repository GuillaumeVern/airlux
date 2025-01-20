#!/bin/bash

sleep 60

# récupération de l'adresse mac pour la stocker dans la base de données
NETINT="$(ip route get 8.8.8.8 | sed -nr 's/.*dev ([^\ ]+).*/\1/p')"
MAC="$(cat /sys/class/net/$NETINT/address)"
echo "Adresse MAC: $MAC"

RSA="$(sudo -i -u tunnel-user cat /home/tunnel-user/.ssh/id_rsa.pub)"
echo "Clé publique: $RSA"

# enregistrement du raspberry pour restaurer les routes traefik si elles sont cassées
curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://g3.south-squad.io:8000/raspberry


# récupération du remote port ssh
REMOTE_SSH_PORT="$(curl -X GET http://g3.south-squad.io:8000/raspberry/$MAC/ssh/remote-port | jq -r '.port')"
echo "Port SSH distant: $REMOTE_SSH_PORT"

# port local ssh
LOCAL_SSH_PORT="$(curl -X GET http://g3.south-squad.io:8000/service/ssh/local-port | jq -r '.port')"
echo "Port SSH local: $LOCAL_SSH_PORT"

# remote port home assistant
REMOTE_HA_PORT="$(curl -X GET http://g3.south-squad.io:8000/raspberry/$MAC/home/remote-port | jq -r '.port')"
echo "Port Home Assistant distant: $REMOTE_HA_PORT"

# port local home assistant
LOCAL_HA_PORT="$(curl -X GET http://g3.south-squad.io:8000/service/home/local-port | jq -r '.port')"
echo "Port Home Assistant local: $LOCAL_HA_PORT"

# ajout de la clé publique du serveur dans authorized_keys pour autoriser la connexion une fois le tunnel établi
# enleve le hostname de l'output de ssh-keyscan
# sudo -u tunnel-user ssh-keyscan -t rsa g3.south-squad.io | awk '{print $2, $3}' >> /home/tunnel-user/.ssh/known_hosts
REMOTE_PUB_KEY="$(sudo -u tunnel-user ssh-keyscan -t rsa g3.south-squad.io)"

if ! grep -q "$REMOTE_PUB_KEY" /home/tunnel-user/.ssh/authorized_keys; then
    echo "$REMOTE_PUB_KEY" | awk '{print $2, $3}' >> /home/tunnel-user/.ssh/authorized_keys
fi



sudo -u tunnel-user autossh -vvv -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -f -N -R "$REMOTE_SSH_PORT:localhost:$LOCAL_SSH_PORT" -R ":$REMOTE_HA_PORT:localhost:$LOCAL_HA_PORT" tunnel-user@g3.south-squad.io -i /home/tunnel-user/.ssh/id_rsa -o StrictHostKeyChecking=no

cd /home/user/airlux/NAT/raspberry-pi
sudo docker compose up -d --force-recreate

while true; do
    # # tunnel ssh pour service ssh
    # sudo -u tunnel-user ssh -Nfvv -R "$REMOTE_SSH_PORT:localhost:$LOCAL_SSH_PORT" tunnel-user@g3.south-squad.io -i /home/tunnel-user/.ssh/id_rsa -o StrictHostKeyChecking=no

    # # tunnel ssh pour service home assistant
    # sudo -u tunnel-user ssh -Nfvv -R ":$REMOTE_HA_PORT:localhost:$LOCAL_HA_PORT" tunnel-user@g3.south-squad.io -i /home/tunnel-user/.ssh/id_rsa -o StrictHostKeyChecking=no
    sleep 60
done