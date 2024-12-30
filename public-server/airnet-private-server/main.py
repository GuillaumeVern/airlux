from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse

app = FastAPI()

class Key(BaseModel):
    key: str


@app.post("/keys")
def add_key(key: Key):
    try:
        with open("/config/.ssh/authorized_keys", "a+") as f:
            if key.key not in f.read():
                f.write(key.key + "\n")
        with open("/config/.ssh/known_hosts", "a+") as f:
            if key.key not in f.read():
                f.write(key.key + "\n")
        return JSONResponse(content={"message": "Key added successfully"}, status_code=201)
    except Exception as e:
        return JSONResponse(content={"message": e}, status_code=500)
