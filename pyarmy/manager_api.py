import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"Hello": "World"}


@app.get("/role")
async def get_role() -> str:
    return "Manager"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9393)
