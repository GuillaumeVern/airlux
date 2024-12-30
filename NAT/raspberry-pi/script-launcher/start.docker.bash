apk update
apk add --no-cache curl
apk add --no-cache openssh
apk add --no-cache jq
apk add --no-cache openrc

rc-update add sshd
rc-service sshd start

curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://airnet-api:8000/raspberry
curl -X POST -H "Content-Type: application/json" -d "{\"Adresse_MAC\":\"$MAC\", \"Pub_Key\": \"$RSA\"}" http://airnet-api:8000/key
PORT="$(curl -X GET http://airnet-api:8000/raspberry/$MAC/port | jq -r '.port')"
ssh -Nfvvvv -R "$PORT:localhost:22" airnet@openssh-server -i /home/tunnel-user/.ssh/id_rsa -o StrictHostKeyChecking=no -o Port=2222