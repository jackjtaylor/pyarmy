import asyncio
from typing import Mapping

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/role")
async def get_role() -> str:
    return "Worker"


@app.post("/get?={task}")
async def get_task(task: Mapping) -> Mapping:
    instructions = task["instructions"]
    result = await asyncio.create_subprocess_exec(instructions)
    return {"result": result.returncode}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9393)
