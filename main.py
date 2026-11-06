import logging, random, time, json, socket
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST


APP_NAME = "paula-fastapi-app"
app = FastAPI()

class LogstashHandler(logging.Handler):
    def __init__(self, host="localhost", port=5001):
        super().__init__()
        self.host, self.port = host, port
        self.sock = None                      # la conexión se abre la primera vez que se necesita

    def emit(self, record):
        # 1. sacar los datos del record
        evento = {
            "@timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc)
                          .isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger_name": record.name,
            "application": APP_NAME,          # ¡clave! con esto Logstash nombra el índice
        }
        # 2. JSON en una línea + salto de línea, convertido a bytes
        linea = (json.dumps(evento) + "\n").encode("utf-8")
        # 3. mandarlo por TCP
        try:
            if self.sock is None:
                self.sock = socket.create_connection((self.host, self.port), timeout=2)
            self.sock.sendall(linea)
        except OSError:
            self.sock = None                  # si se cayó la conexión, se reintenta en el próximo log
            self.handleError(record)

logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.INFO)
logger.addHandler(LogstashHandler())          # a Logstash
logger.addHandler(logging.StreamHandler())    # y también a la consola, para que lo veas

REQUESTS = Counter("app_requests_total", "Peticiones por endpoint", ["endpoint"])
ERRORS  = Counter("app_errors_total", "Errores por endpoint", ["endpoint"])
LATENCY = Histogram("app_request_seconds", "Duración de las peticiones", ["endpoint"])

@app.get("/hola")
def hola():
    REQUESTS.labels("hola").inc()
    with LATENCY.labels("hola").time():
        time.sleep(random.uniform(0.05, 0.3))
        logger.info("Saludando desde Python")
    return {"mensaje": "Hola desde FastAPI"}

@app.get("/falla")
def falla():
    REQUESTS.labels("falla").inc()
    ERRORS.labels("falla").inc()
    logger.error("Algo falló en /falla")
    raise HTTPException(status_code=500, detail="Error simulado")