from typing import Union
from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
from fastapi.responses import JSONResponse
from random import randint

import mysql.connector


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
        cursor.execute("SELECT Remote_Port FROM Raspberry")
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

@app.get("/raspberry/{mac}/port")
def get_port(mac: str):
    try:
        result = get_raspberry(mac)

        if result == False:
            return JSONResponse(content={"message": "Raspberry not found"}, status_code=404)

        return JSONResponse(content={"port": result[2]}, status_code=200)
    except Exception as e:
        db.reconnect(attempts=1, delay=0)
        return JSONResponse(content={"message": e}, status_code=500)

@app.post("/raspberry")
def create_raspberry(raspberry: Raspberry, request: Request):
    raspberry.Adresse_MAC = format_mac(raspberry.Adresse_MAC)
    isPresent = get_raspberry(raspberry.Adresse_MAC)
    if isPresent != False:
        return JSONResponse(content={"message": "Raspberry already exists"}, status_code=409)
    try:
        cursor = db.cursor(prepared=True)
        port = get_free_port()
        cursor.execute("INSERT INTO Raspberry (Adresse_MAC, Adresse_ip, Remote_Port) VALUES (%s, %s, %s)", (raspberry.Adresse_MAC, request.client.host, port))
        db.commit()

        # enregistrement de la clé publique
        post_rsa(raspberry, request)

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
    mac = mac.replace("%3A", ":")
    return mac