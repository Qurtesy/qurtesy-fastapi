from fastapi import FastAPI

app = FastAPI()

@app.get("/", tags=["home"])
async def root():
    return { "message": "Hello World" }

@app.get("/mS2", tags=["mS2"])
async def root():
    return { "message": "Hello World from microService 2" }
