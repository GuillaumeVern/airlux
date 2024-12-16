from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

import mysql.connector


class Raspberry(BaseModel):
    Adresse_MAC: str
    Adresse_ip: str
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
    cursor.execute("SELECT * FROM Raspberry WHERE Adresse_MAC = %s", (mac,))
    result = cursor.fetchall()
    if (len(result) == 0):
        return false
    return result[0]

@app.post("/raspberry")
def create_raspberry(raspberry: Raspberry):
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO Raspberry (Adresse_MAC, Adresse_ip, Pub_Key) VALUES (%s, %s, %s)", (raspberry.Adresse_MAC, raspberry.Adresse_ip, raspberry.Pub_Key))
        db.commit()
        return JSONResponse(content={"message": "Raspberry created successfully"}, status_code=201)
    except Exception as e:
        return JSONResponse(content={"message": e}, status_code=500)

