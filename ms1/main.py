from fastapi import FastAPI

app = FastAPI()

@app.get("/", tags=["home"])
async def root():
    return { "message": "Hello World" }

@app.get("/mS1", tags=["mS1"])
async def root():
    return { "message": "Hello World from microService 1" }
