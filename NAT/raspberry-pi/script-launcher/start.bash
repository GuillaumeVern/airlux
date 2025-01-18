#!/bin/bash
apt-get update
apt-get upgrade -y
apt-get install wget udisks2 libglib2.0-bin network-manager dbus systemd-journal-remote systemd-resolved -y
apt-get install -y jq
apt-get install -y curl
apt-get install -y openssh-server
apt-get install -y autossh

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
NETINT="$(ip route get 8.8.8.8 | sed -nr 's/.*dev ([^\ ]+).*/\1/p')"
MAC="$(cat /sys/class/net/$NETINT/address)"
echo "Adresse MAC: $MAC"


# démarrage des différents services ssh
sudo systemctl enable sshd
sudo systemctl start sshd
sudo systemctl enable ssh
sudo systemctl start ssh

# configuration de sshd
sudo sed -i 's/#HostKey \/etc\/ssh\/ssh_host_rsa_key/HostKey \/home\/tunnel-user\/.ssh\/id_rsa/g' /etc/ssh/sshd_config
sudo sed -i 's/# AuthorizedKeysFile/AuthorizedKeysFile/g' /etc/ssh/sshd_config
sudo sed -i 's/#AllowTcpForwarding yes/AllowTcpForwarding yes/g' /etc/ssh/sshd_config
sudo sed -i 's/#GatewayPorts no/GatewayPorts yes/g' /etc/ssh/sshd_config
sudo sed -i 's/#TCPKeepAlive yes/TCPKeepAlive yes/g' /etc/ssh/sshd_config
sudo sed -i 's/#ClientAliveInterval 0/ClientAliveInterval 30/g' /etc/ssh/sshd_config
sudo sed -i 's/#ClientAliveCountMax 3/ClientAliveCountMax 3/g' /etc/ssh/sshd_config

# redémarrage de sshd pour prendre en compte les modifications
sudo systemctl restart sshd

# récupération de la clé publique pour l'envoyer au serveur
sudo -u tunnel-user ls -la /home/tunnel-user/.ssh
RSA="$(sudo -i -u tunnel-user cat /home/tunnel-user/.ssh/id_rsa.pub)"
echo "Clé publique: $RSA"

# enregistrement du raspberry dans la bdd + attribution du port
curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://g3.south-squad.io:8000/raspberry

# enregistrement de la clé publique dans authorized_keys sur le serveur
curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://g3.south-squad.io:8000/key

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# if the systemd service does not exist, copy the script to the correct folder and create a systemd service for it

sudo cp $SCRIPT_DIR/ssh_tunnel.bash /usr/bin/start_tunnel
if [ ! -f /etc/systemd/system/ssh_tunnel.service ]; then
    sudo cp -f $SCRIPT_DIR/ssh_tunnel.service /etc/systemd/system/ssh_tunnel.service
    sudo chmod +x /usr/bin/start_tunnel
    sudo systemctl daemon-reload
    sudo systemctl enable ssh_tunnel
    sudo systemctl start ssh_tunnel
fi


# on installe docker si ce n'est pas déjà fait
if ! [ -x "$(command -v docker)" ]; then
    sleep 10
    sudo curl -fsSL https://get.docker.com -o ~/get-docker.sh
    sudo sh ~/get-docker.sh
fi

# installation de homeassistant
wget https://github.com/home-assistant/os-agent/releases/download/1.2.2/os-agent_1.2.2_linux_x86_64.deb
dpkg -i os-agent_1.2.2_linux_x86_64.deb
wget https://github.com/home-assistant/supervised-installer/releases/latest/download/homeassistant-supervised.deb
dpkg -i homeassistant-supervised.deb


# on lance les services locaux
cd $SCRIPT_DIR
cd ../
cp -f ../esp32-devices/simulation/.env.example ../esp32-devices/simulation/.env
sudo docker compose up -d --force-recreate

