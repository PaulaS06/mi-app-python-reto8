from fastapi import FastAPI, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

APP_NAME = "paula-fastapi-app"
app = FastAPI()

REQUESTS = Counter("app_requests_total", "Peticiones por endpoint", ["endpoint"])

@app.get("/hola")
def hola():
    REQUESTS.labels("hola").inc()
    return {"mensaje": "Hola desde FastAPI"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)