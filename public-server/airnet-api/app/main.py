from typing import Union
from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
from fastapi.responses import JSONResponse
from random import randint
import yaml
import logging

import mysql.connector

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)


class Raspberry(BaseModel):
    Adresse_MAC: str
    Pub_Key: str

app = FastAPI()

db = mysql.connector.connect(
  host="mysql-db",
  user="airlux",
  password="airlux",
  database="airlux"
)



@app.get("/raspberry")
def get_raspberries():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Raspberry")
        result = cursor.fetchall()
        return result
    except Exception as e:
        db.reconnect(attempts=1, delay=0)
        return JSONResponse(content={"message": e}, status_code=500)

@app.get("/raspberry/{mac}")
def get_raspberry(mac: str):
    try:
        mac = format_mac(mac)

        cursor = db.cursor(prepared=True)
        cursor.execute("SELECT * FROM Raspberry WHERE Adresse_MAC = %s LIMIT 1", (mac,))
        result = cursor.fetchall()

        if (len(result) < 1):
            return False
        return result[0]
    except Exception as e:
        db.reconnect(attempts=1, delay=0)
        return JSONResponse(content={"message": e}, status_code=500)

# cette route n'est pas utilisée mais elle existe juste pour les tests
@app.get("/port")
def get_free_port():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT Remote_Port FROM Raspberry_has_Service")
        result = cursor.fetchall()
        port = randint(10000, 20000)

        attempts = 0
        while port in result and attempts < 100:
            port = randint(10000, 20000)
            attempts += 1

        if attempts >= 100:
            return False

        return port
    except Exception as e:
        db.reconnect(attempts=1, delay=0)
        return JSONResponse(content={"message": e}, status_code=500)

def get_raspberry_service_port(raspberry_id: int, service: str):
    try:
        cursor = db.cursor(prepared=True)
        cursor.execute("SELECT Remote_Port FROM Raspberry_has_Service WHERE Id_Raspberry = %s AND Id_Service = (SELECT Id_Service FROM Service WHERE Prefixe = %s)", (raspberry_id, service))
        result = cursor.fetchall()

        if (len(result) < 1):
            return False
        return result[0][0]
    except Exception as e:
        db.reconnect(attempts=1, delay=0)
        return JSONResponse(content={"message": e}, status_code=500)

@app.get("/service/{service}/local-port")
def get_local_port(service: str):
    try:
        cursor = db.cursor(prepared=True)
        cursor.execute("SELECT Local_Port FROM Service WHERE Prefixe = %s", (service,))
        result = cursor.fetchall()

        if (len(result) < 1):
            return JSONResponse(content={"message": "Service not found"}, status_code=404)
        return JSONResponse(content={"port": result[0][0]}, status_code=200)
    except Exception as e:
        db.reconnect(attempts=1, delay=0)
        return JSONResponse(content={"message": e}, status_code=500)

@app.get("/raspberry/{mac}/{service}/remote-port")
def get_port(mac: str, service: str):
    try:
        raspberry = get_raspberry(mac)

        if raspberry == False:
            return JSONResponse(content={"message": "Raspberry not found"}, status_code=404)

        remote_port = get_raspberry_service_port(raspberry[0], service)

        if remote_port == False:
            return JSONResponse(content={"message": "Service not found"}, status_code=404)
            
        return JSONResponse(content={"port": remote_port}, status_code=200)
    except Exception as e:
        db.reconnect(attempts=1, delay=0)
        return JSONResponse(content={"message": e}, status_code=500)

def randint_to_str(random_integer: int):
    take_1_or_2 = randint(1, 2) == 1
    prefixe = ""
    i = 0
    while i < len(str(random_integer)) - 1:
        if take_1_or_2 is True:
            int_prefixe = int(str(random_integer)[i])
            prefixe += chr(int_prefixe % 26 + 97)
            i += 1
            take_1_or_2 = randint(1, 2) == 1
        else:
            int_prefixe = int(str(random_integer)[i:i+2])
            prefixe += chr(int_prefixe % 26 + 97)
            i += 2
            take_1_or_2 = randint(1, 2) == 1
    return prefixe

# generation d'un prefixe aleatoire pour identifier les raspberry
def get_free_prefixe():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT Prefixe FROM Raspberry")
        result = cursor.fetchall()
        prefixe = randint(100000000000, 999999999999)
        prefixe = randint_to_str(prefixe)

        attempts = 0
        while prefixe in result and attempts < 100:
            prefixe = randint(100000000000, 999999999999)
            prefixe = randint_to_str(prefixe)
            attempts += 1

        if attempts >= 100:
            return False

        return prefixe
    except Exception as e:
        db.reconnect(attempts=1, delay=0)
        return JSONResponse(content={"message": e}, status_code=500)


@app.post("/raspberry")
def create_raspberry(raspberry: Raspberry, request: Request):
    raspberry.Adresse_MAC = format_mac(raspberry.Adresse_MAC)
    isPresent = get_raspberry(raspberry.Adresse_MAC)
    try:
        cursor = db.cursor(prepared=True)
        if isPresent != False:
            # configuration de traefik
            ports_distants = []
            id_raspberry = isPresent[0]
            cursor.execute("SELECT * FROM Raspberry_has_Service WHERE Id_Raspberry = %s", (id_raspberry,))
            services = cursor.fetchall()
            for service in services:
                # on fait une liste de tous les ports distants exposés par un tunnel ssh
                ports_distants.append(service[2])
                
            prefixe = isPresent[3]
            assert prefixe is not None
            add_traefik_route(prefixe, ports_distants)
            return JSONResponse(content={"message": "Raspberry already exists"}, status_code=409)
        
        
        prefixe = get_free_prefixe()
        cursor.execute("INSERT INTO Raspberry (Adresse_MAC, Adresse_ip, Prefixe) VALUES (%s, %s, %s)", (raspberry.Adresse_MAC, request.client.host, prefixe))
        db.commit()

        # enregistrement de la clé publique
        post_rsa(raspberry, request)

        # id du raspberry
        dbraspberry = get_raspberry(raspberry.Adresse_MAC)
        id_raspberry = dbraspberry[0]

        # enregistrement des services
        cursor.execute("SELECT * FROM Service")
        services = cursor.fetchall()
        for service in services:
            if service[2] in ["ssh", "home"]:
                port = get_free_port()
                cursor.execute("INSERT INTO Raspberry_has_Service (Id_Raspberry, Id_Service, Remote_Port) VALUES (%s, %s, %s)", (id_raspberry, service[0], port))
                db.commit()

        # configuration de traefik
        ports_distants = []
        cursor.execute("SELECT * FROM Raspberry_has_Service WHERE Id_Raspberry = %s", (id_raspberry,))
        services = cursor.fetchall()
        for service in services:
            # on fait une liste de tous les ports distants exposés par un tunnel ssh
            ports_distants.append(service[2])
            
        prefixe = dbraspberry[3]
        add_traefik_route(prefixe, ports_distants)
        

        return JSONResponse(content={"message": "Raspberry created successfully"}, status_code=201)
    except Exception as e:
        return JSONResponse(content={"message": e}, status_code=500)


@app.get("/key")
def get_rsa():
    response = requests.get("http://airnet-private-server:7880/key")
    key = response.json().get("key")
    return key

@app.post("/key")
def post_rsa(raspberry: Raspberry, request: Request):
    requests.post("http://airnet-private-server:7880/keys", json={"key": raspberry.Pub_Key})
    return JSONResponse(content={"message": "Key added successfully"}, status_code=201)

def format_mac(mac: str):
    mac = mac.lower()
    mac = mac.replace("-", ":")
    mac = mac.replace("%3a", ":")
    return mac

def load_dynamic_config_file():
    try:
        with open("/app/app/dynamic.yml", "r") as stream:
            try:
                data = yaml.safe_load(stream)
                stream.close()
                if data is None:
                    data = {"http": {"routers": {}, "services": {}}}
                return data
            except yaml.YAMLError as exc:
                return JSONResponse(content={"message": exc}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"message": e}, status_code=500)
    
def add_traefik_route(prefixe: str, ports_distants: list):
    try:
        data = load_dynamic_config_file()
        for port_distant in ports_distants:
            service_name = get_service_name(port_distant)
            data["http"]["routers"][f"{service_name}-{prefixe}"] = {
                "rule": f"Host(`{service_name}.{prefixe}.g3.south-squad.io`)",
                "service": f"{service_name}-{prefixe}",
                "entryPoints": ["websecure"],
                "tls": {"certResolver": "letsencrypt"}
            }
            data["http"]["services"][f"{service_name}-{prefixe}"] = {
                "loadBalancer": {
                    "servers": [
                        {"url": f"http://localhost:{port_distant}/"}
                    ]
                }
            }
        file = open("/app/app/dynamic.yml", "w")
        yaml.dump(data, file)
    except Exception as e:
        return JSONResponse(content={"message": e}, status_code=500)

def get_service_name(port_distant: int):
    try:
        cursor = db.cursor(prepared=True)
        cursor.execute("SELECT Id_Service FROM Raspberry_has_Service WHERE Remote_Port = %s", (port_distant,))
        result = cursor.fetchall()

        if (len(result) < 1):
            return False

        cursor.execute("SELECT Prefixe FROM Service WHERE Id_Service = %s", (result[0][0],))
        result = cursor.fetchall()

        if (len(result) < 1):
            return False
        return result[0][0]
    except Exception as e:
        db.reconnect(attempts=1, delay=0)
        return JSONResponse(content={"message": e}, status_code=500)