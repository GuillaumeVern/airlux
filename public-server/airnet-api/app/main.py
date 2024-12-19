from typing import Union
from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
from fastapi.responses import JSONResponse

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
def read_root():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Raspberry")
    result = cursor.fetchall()
    return result

@app.get("/raspberry/{mac}")
def read_root(mac: str):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Raspberry JOIN Ping ON Ping.Adresse_MAC = Raspberry.Adresse_MAC JOIN Raspberry_has_Service ON Raspberry.Adresse_MAC = Raspberry_has_Service.Adresse_MAC JOIN Service ON Raspberry_has_Service.Id_Service = Service.Id_Service WHERE Adresse_MAC = %s", (mac,))
    result = cursor.fetchall()
    if (len(result) == 0):
        return false
    return result[0]

@app.post("/raspberry")
def create_raspberry(raspberry: Raspberry, request: Request):
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO Raspberry (Adresse_MAC, Adresse_ip) VALUES (%s, %s)", (raspberry.Adresse_MAC, request.client.host))
        db.commit()

        # enregistrement de la clé publique
        requests.post("http://airnet-private-server:7880/keys", json={"key": raspberry.Pub_Key})

        return JSONResponse(content={"message": "Raspberry created successfully"}, status_code=201)
    except Exception as e:
        return JSONResponse(content={"message": e}, status_code=500)


