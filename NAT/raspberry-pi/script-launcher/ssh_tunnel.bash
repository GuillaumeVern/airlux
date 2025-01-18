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

sudo -u tunnel-user autossh -vvv -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -f -N -R "$REMOTE_SSH_PORT:localhost:$LOCAL_SSH_PORT" -R ":$REMOTE_HA_PORT:localhost:$LOCAL_HA_PORT" tunnel-user@g3.south-squad.io -i /home/tunnel-user/.ssh/id_rsa -o StrictHostKeyChecking=no

while true; do
    sleep 60
done