apk update
apk add --no-cache curl
apk add --no-cache openssh
apk add --no-cache jq
apk add --no-cache openrc

rc-update add sshd
echo "n" | ssh-keygen -t rsa -b 4096 -f /etc/ssh/raspberry_rsa -N ""

MAC="$(cat /sys/class/net/eth0/address)"
echo "Adresse MAC: $MAC"

rc-service sshd start

ls /etc/ssh
RSA="$(cat /etc/ssh/raspberry_rsa.pub)"
echo "Clé publique: $RSA"





curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://212.83.130.156:8000/raspberry
# curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://airnet-api:8000/raspberry

curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://212.83.130.156:8000/key
# curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://airnet-api:8000/key




PORT="$(curl -X GET http://212.83.130.156:8000/raspberry/$MAC/port | jq -r '.port')"
# PORT="$(curl -X GET http://airnet-api:8000/raspberry/$MAC/port | jq -r '.port')"
echo "Port: $PORT"

SRV_RSA="$(curl -X GET http://212.83.130.156:8000/key)"
# SRV_RSA="$(curl -X GET http://airnet-api:8000/key)"
echo "Clé publique serveur: $SRV_RSA"
# echo "$SRV_RSA" > /etc/ssh/known_hosts

ssh -Nfvvvv -R "$PORT:localhost:22" airnet@openssh-server -i /etc/ssh/raspberry_rsa -o StrictHostKeyChecking=no -o Port=2222

sleep 2000