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
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Raspberry")
    result = cursor.fetchall()
    return result

@app.get("/raspberry/{mac}")
def get_raspberry(mac: str):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Raspberry WHERE Adresse_MAC = %s LIMIT 1", (mac,))
    result = cursor.fetchall()

    if (len(result) < 1):
        mac = mac.replace(":", "-")
        cursor.execute("SELECT * FROM Raspberry WHERE Adresse_MAC = %s LIMIT 1", (mac,))
        result = cursor.fetchall()

    if (len(result) < 1):
        return False
    return result[0]

def get_free_port():
    cursor = db.cursor()
    cursor.execute("SELECT Remote_Port FROM Raspberry")
    result = cursor.fetchall()
    port = randint(10000, 20000)

    # hmmmmmmmm... potentielle récursion infinie si tous les ports sont pris... mais bon je peux vivre avec
    if port in result:
        port = get_free_port()

    return port

@app.get("/raspberry/{mac}/port")
def get_port(mac: str):
    result = get_raspberry(mac)

    if result == False:
        return JSONResponse(content={"message": "Raspberry not found"}, status_code=404)

    return JSONResponse(content={"port": result[2]}, status_code=200)

@app.post("/raspberry")
def create_raspberry(raspberry: Raspberry, request: Request):
    isPresent = get_raspberry(raspberry.Adresse_MAC)
    if isPresent != False:
        return JSONResponse(content={"message": "Raspberry already exists"}, status_code=409)
    try:
        cursor = db.cursor()
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
