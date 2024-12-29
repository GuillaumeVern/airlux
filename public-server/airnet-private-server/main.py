from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse

app = FastAPI()

class Key(BaseModel):
    key: str

def create_file_if_not_exists():
    try:
        with open("/config/.ssh/authorized_keys", "x") as f:
            f.write("")
        with open("/config/.ssh/known_hosts", "x") as f:
            f.write("")
    except:
        pass


@app.post("/keys")
def add_key(key: Key):
    try:
        create_file_if_not_exists()
        with open("/config/.ssh/authorized_keys", "a") as f:
            f.write(key.key + "\n")
        with open("/config/.ssh/known_hosts", "a") as f:
            f.write(key.key + "\n")
        return JSONResponse(content={"message": "Key added successfully"}, status_code=201)
    except Exception as e:
        return JSONResponse(content={"message": e}, status_code=500)
