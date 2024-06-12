from ipaddress import IPv4Address

import uvicorn
from aiohttp import ClientSession, ClientTimeout
from fastapi import FastAPI, Request
from tinydb import TinyDB, Query

database = TinyDB("db.json")
app = FastAPI()


@app.get("/role")
async def get_role() -> str:
    return "Manager"


@app.post("/send/{task}")
async def send_task(task: str):
    workers = database.table("workers")
    worker_responses = {}

    for worker in workers.all():
        async with ClientSession(timeout=ClientTimeout(total=0.25)) as session:
            # This uses unencrypted HTTP to set a URL to request
            port = 9255
            request = f"http://{worker["ip"]}:{port}/get_task?=ipconfig"

            # This requests the address for a role response
            async with session.post(request) as response:
                code = await response.text()
                worker_responses[worker["ip"]] = code

    print(worker_responses)


@app.get("/connect")
async def connect(request: Request):
    """
    This function connects a new worker to this manager.
    :param request: The HTTP request, with the IP of the request included
    """
    if not request.client:
        return

    ip = IPv4Address(request.client.host)

    configuration = {"ip": str(ip), "status": "online"}

    workers = database.table("workers")
    worker = Query()
    existing = workers.search(worker.ip == str(ip))

    if not existing:
        workers.insert(configuration)
    else:
        workers.update(configuration, worker.ip == str(ip))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9255)
