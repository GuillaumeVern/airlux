from typing import Union

from fastapi import FastAPI

import mysql.connector

app = FastAPI()

db = mysql.connector.connect(
  host="localhost",
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


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}