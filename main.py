from typing import Union
from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/api/")
def root():
    return "server up and running..."


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

# reminder not to use reload in production