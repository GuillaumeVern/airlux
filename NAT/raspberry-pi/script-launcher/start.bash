apk update
apk add --no-cache curl
apk add --no-cache openssh
apk add --no-cache jq
apk add --no-cache openrc

apt-get install -y jq

rc-update add sshd

MAC="$(cat /sys/class/net/eth0/address)"
echo "Adresse MAC: $MAC"

rc-service sshd start
sudo systemctl enable sshd
sudo systemctl start sshd
sudo systemctl enable ssh
sudo systemctl start ssh



echo "n" | ssh-keygen -t rsa -b 4096 -f /etc/ssh/id_rsa -N ""

ls /etc/ssh
RSA="$(ssh-keyscan -t rsa localhost)"
echo "Clé publique: $RSA"



curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://212.83.130.156:8000/raspberry
# curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://airnet-api:8000/raspberry

curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://212.83.130.156:8000/key
# curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://airnet-api:8000/key




PORT="$(curl -X GET http://212.83.130.156:8000/raspberry/$MAC/port | jq -r '.port')"
# PORT="$(curl -X GET http://airnet-api:8000/raspberry/$MAC/port | jq -r '.port')"
echo "Port: $PORT"

ssh-keyscan -t rsa 212.83.130.156 >> /home/user/.ssh/authorized_keys


sudo -u user ssh -Nfvvvv -R "$PORT:localhost:22" g3@212.83.130.156 -i /etc/ssh/id_rsa -o StrictHostKeyChecking=no
# ssh -Nfvvvv -R "$PORT:localhost:22" airnet@openssh-server -i /etc/ssh/id_rsa -o StrictHostKeyChecking=no -o Port=2222