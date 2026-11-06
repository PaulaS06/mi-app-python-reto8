import logging, random, time, json, socket
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST


APP_NAME = "paula-fastapi-app"
app = FastAPI()



REQUESTS = Counter("app_requests_total", "Peticiones por endpoint", ["endpoint"])
ERRORS  = Counter("app_errors_total", "Errores por endpoint", ["endpoint"])
LATENCY = Histogram("app_request_seconds", "Duración de las peticiones", ["endpoint"])

@app.get("/hola")
def hola():
    REQUESTS.labels("hola").inc()
    return {"mensaje": "Hola desde FastAPI"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)