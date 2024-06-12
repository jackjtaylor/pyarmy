from ipaddress import IPv4Address
from typing import Mapping

import uvicorn
from fastapi import FastAPI, Request
from tinydb import TinyDB

database = TinyDB("db.json")
app = FastAPI()


@app.get("/role")
async def get_role() -> str:
    return "Manager"


@app.post("/send?={task}")
async def send_task(task: Mapping):
    pass


@app.get("/connect")
async def connect(request: Request):
    """
    This function connects a new worker to this manager.
    :param request: The HTTP request, with the IP of the request included
    """
    if not request.client:
        return

    ip = IPv4Address(request.client.host)
    configuration = {"ip": ip.exploded, "status": "online"}

    workers = database.table("workers")
    workers.insert(configuration)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9255)
