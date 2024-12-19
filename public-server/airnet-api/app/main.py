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
    cursor.execute("SELECT * FROM Raspberry JOIN Ping ON Ping.Adresse_MAC = Raspberry.Adresse_MAC JOIN Raspberry_has_Service ON Raspberry.Adresse_MAC = Raspberry_has_Service.Adresse_MAC JOIN Service ON Raspberry_has_Service.Id_Service = Service.Id_Service WHERE Adresse_MAC = %s", (mac,))
    result = cursor.fetchall()
    if (len(result) == 0):
        return false
    return result[0]

def get_free_port():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Raspberry")
    result = cursor.fetchall()
    port = randint(10000, 20000)

    # on vérifie que le port n'est pas deja pris, très lent mais bon... ¯\_(ツ)_/¯ 
    i = 0
    while i < len(result):
        if result[i][2] == port:
            port = randint(10000, 20000)
            i = 0
        i += 1

    return port

@app.get("/raspberry/{mac}/port")
def get_port(mac: str):
    cursor = db.cursor()
    cursor.execute("SELECT Remote_Port FROM Raspberry WHERE Adresse_MAC = %s LIMIT 1", (mac,))
    result = cursor.fetchone()
    print(result)
    return JSONResponse(content={"port": result}, status_code=200)

@app.post("/raspberry")
def create_raspberry(raspberry: Raspberry, request: Request):
    try:
        cursor = db.cursor()
        port = get_free_port()
        cursor.execute("INSERT INTO Raspberry (Adresse_MAC, Adresse_ip, Remote_Port) VALUES (%s, %s, %s)", (raspberry.Adresse_MAC, request.client.host, port))
        db.commit()

        # enregistrement de la clé publique
        requests.post("http://airnet-private-server:7880/keys", json={"key": raspberry.Pub_Key})

        return JSONResponse(content={"message": "Raspberry created successfully"}, status_code=201)
    except Exception as e:
        return JSONResponse(content={"message": e}, status_code=500)


