apk update
apk add --no-cache curl
apk add --no-cache openssh
apk add --no-cache jq
apk add --no-cache openrc

rc-update add sshd
rc-service sshd start

MAC="$(cat /sys/class/net/eth0/address)"
echo "Adresse MAC: $MAC"

ssh-keygen -t rsa -b 4096 -f raspberry_rsa -N ""

RSA="$(cat ./raspberry_rsa.pub)"
echo "Clé publique: $RSA"





curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://212.83.130.156:8000/raspberry

echo "Raspberry-pi enregistré"


PORT="$(curl -X GET http://212.83.130.156:8000/raspberry/$MAC/port | jq -r '.port')"
echo "Port: $PORT"

ssh -Nf -R "$PORT:localhost:22" root@212.83.130.156