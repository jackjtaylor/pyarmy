import uvicorn
from fastapi import FastAPI, Request
import pickledb

database = pickledb.load("test.json", True)
app = FastAPI()


@app.get("/")
async def root():
    return {"Hello": "World"}


@app.get("/role")
async def get_role() -> str:
    return "Manager"


@app.post("/send/{cmd}")
async def send_cmd(cmd: str):
    workers = database.table("workers")


@app.get("/connect")
async def get_new_worker(request: Request):
    if not request.client:
        return

    configuration = {"status": "Online", "uptime": 0}
    database.dcreate("workers")
    database.dadd("workers", (request.client.host, configuration))
    # Can't use TinyDB as strings can't be IDs


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9255)
