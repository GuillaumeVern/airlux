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



echo "n" | sudo -i -u tunnel-user ssh-keygen -t rsa -b 4096 -f /home/tunnel-user/.ssh/id_rsa -N ""

sudo -i -u tunnel-user ls -la /home/tunnel-user/.ssh
RSA="$(sudo -i -u tunnel-user cat /home/tunnel-user/.ssh/id_rsa.pub)"
echo "Clé publique: $RSA"



curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://212.83.130.156:8000/raspberry
# curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://airnet-api:8000/raspberry

curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://212.83.130.156:8000/key
# curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://airnet-api:8000/key




PORT="$(curl -X GET http://212.83.130.156:8000/raspberry/$MAC/port | jq -r '.port')"
# PORT="$(curl -X GET http://airnet-api:8000/raspberry/$MAC/port | jq -r '.port')"
echo "Port: $PORT"

sudo -i -u tunnel-user ssh-keyscan -t rsa 212.83.130.156 >> /home/tunnel-user/.ssh/authorized_keys

sleep 5

sudo -u tunnel-user ssh -Nfvvvv -R "$PORT:localhost:22" tunnel-user@212.83.130.156 -i /home/tunnel-user/.ssh/id_rsa -o StrictHostKeyChecking=no
# ssh -Nfvvvv -R "$PORT:localhost:22" airnet@openssh-server -i /home/tunnel-user/.ssh/id_rsa -o StrictHostKeyChecking=no -o Port=2222