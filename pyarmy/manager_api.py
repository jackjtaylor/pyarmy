import uvicorn
from fastapi import FastAPI, Request
from tinydb import TinyDB

db = TinyDB("db.json")
app = FastAPI()


@app.get("/")
async def root():
    return {"Hello": "World"}


@app.get("/role")
async def get_role() -> str:
    return "Manager"


@app.post("/send/{cmd}")
async def send_cmd(cmd: str):
    table = db.table("workers")
    workers = table.all()
    for w in workers:
        print(w.keys())
        pass


@app.get("/connect")
async def get_new_worker(request: Request):
    if not request.client:
        return

    workers = db.table("workers")
    configuration = {"status": "Online", "uptime": 0}
    workers.insert({request.client.host: configuration})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9255)
