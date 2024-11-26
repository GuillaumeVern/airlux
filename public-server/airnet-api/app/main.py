from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

import mysql.connector


class Raspberry(BaseModel):
    Adresse_MAC: str | None = None
    Adresse_ip: str
    Pub_Key: str | None = None

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

@app.get("/raspberry/{id}")
def read_root(id: int):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Raspberry WHERE Id_Raspberry = %s", (id,))
    result = cursor.fetchall()
    if (len(result) == 0):
        return "No Raspberry found with this id"
    return result[0]

@app.post("/raspberry")
def create_raspberry(raspberry: Raspberry):
    cursor = db.cursor()
    cursor.execute("INSERT INTO Raspberry (Adresse_MAC, Adresse_ip, Pub_Key) VALUES (%s, %s, %s)", (raspberry.Adresse_MAC, raspberry.Adresse_ip, raspberry.Pub_Key))
    db.commit()
    return


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}