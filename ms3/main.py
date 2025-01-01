from fastapi import FastAPI

app = FastAPI()

@app.get("/", tags=["home"])
async def root():
    return { "message": "Hello World" }

@app.get("/mS3", tags=["mS3"])
async def root():
    return { "message": "Hello World from microService 3" }
