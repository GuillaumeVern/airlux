#!/bin/bash
apt-get update
apt-get install -y jq

# on crée l'utilisateur tunnel-user s'il n'existe pas
# -m pour s'assurer que le répertoire home est créé
id -u tunnel-user &>/dev/null || useradd tunnel-user -p tuiop14!! -m 

# création du répertoires nécessaires à l'authentification par clé rsa
# on utiliser l'utilisateur tunnel-user pour éviter les problèmes de permissions
sudo -u tunnel-user mkdir -p /home/tunnel-user/.ssh
sudo -u tunnel-user touch /home/tunnel-user/.ssh/authorized_keys
sudo -u tunnel-user touch /home/tunnel-user/.ssh/known_hosts
sudo -u tunnel-user chmod 700 /home/tunnel-user/.ssh
sudo -u tunnel-user chmod 600 /home/tunnel-user/.ssh/authorized_keys
sudo -u tunnel-user chmod 600 /home/tunnel-user/.ssh/known_hosts

# génération des clés rsa
# echo n pour ne pas overwrite la clé existante
echo "n" | sudo -u tunnel-user ssh-keygen -t rsa -b 4096 -f /home/tunnel-user/.ssh/id_rsa -N ""


# récupération de l'adresse mac pour la stocker dans la base de données
MAC="$(cat /sys/class/net/eth0/address)"
echo "Adresse MAC: $MAC"

# démarrage des différents services ssh
sudo systemctl enable sshd
sudo systemctl start sshd
sudo systemctl enable ssh
sudo systemctl start ssh

# configuration de sshd
sudo sed -i 's/#HostKey \/etc\/ssh\/ssh_host_rsa_key/HostKey \/home\/tunnel-user\/.ssh\/id_rsa/g' /etc/ssh/sshd_config
sudo sed -i 's/# AuthorizedKeysFile/AuthorizedKeysFile/g' /etc/ssh/sshd_config

# redémarrage de sshd pour prendre en compte les modifications
sudo /etc/init.d/ssh restart

# récupération de la clé publique pour l'envoyer au serveur
sudo -u tunnel-user ls -la /home/tunnel-user/.ssh
RSA="$(sudo -i -u tunnel-user cat /home/tunnel-user/.ssh/id_rsa.pub)"
echo "Clé publique: $RSA"

# enregistrement du raspberry dans la bdd + attribution du port
curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://212.83.130.156:8000/raspberry

# enregistrement de la clé publique dans authorized_keys sur le serveur
curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://212.83.130.156:8000/key

# récupération du port attribué
PORT="$(curl -X GET http://212.83.130.156:8000/raspberry/$MAC/port | jq -r '.port')"
echo "Port: $PORT"

# ajout de la clé publique du serveur dans authorized_keys pour autoriser la connexion une fois le tunnel établi
# enleve le hostname de l'output de ssh-keyscan
sudo -u tunnel-user ssh-keyscan -t rsa 212.83.130.156 | awk '{print $2, $3}' >> /home/tunnel-user/.ssh/known_hosts

# on s'assure que les commandes précédentes ont bien été enregistrées par le serveur avant de créer le tunnel
wait

sudo -u tunnel-user ssh -Nfvvvv -R "$PORT:localhost:22" tunnel-user@212.83.130.156 -i /home/tunnel-user/.ssh/id_rsa -o StrictHostKeyChecking=no