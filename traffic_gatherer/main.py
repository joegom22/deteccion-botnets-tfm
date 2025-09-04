import os
import logging

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse

from pydantic import BaseModel, Field

from src.gather import gather_traffic
from src.verify import token_verification_dependency

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Gauge

limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger("uvicorn")

app = FastAPI(
    title="IoT Traffic Gathering Service",
    description="""<p> Microservice for network traffic gathering. This service captures network traffic via tcpdump and processes it into a PCAP file. Then it processes the PCAP file to extract flow information combining python algorithm and also tshark and 
    outputs the flow results raw in CSV format and condensed flow data also in CSV format. </p> <p> The resulting 3 files are saved in the shared directory (/app/shared) and can be accessed by other services or users. </p>""",
    version="1.0.0"
)

Instrumentator().instrument(app).expose(app)

app.state.limiter = limiter

GATHERER_CSV_FILES = Gauge(
    "gather_csv_size",
    "Tamaño en bytes del último CSV generado por gather_traffic."
)
GATHERER_CSV_ROWS = Gauge(
    "gather_csv_rows",
    "Número de filas del último CSV generado por gather_traffic."
)

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Request blocked."}
    )

class GatheringRequest(BaseModel):
    duration: int = Field("3600", description="Duration of the traffic gathering (defaults to: 1h)", example=120)

def _count_csv_rows(file_path: str) -> int:
    """
    Counts the number of rows in a CSV file except header.

    Args:
        file_path (str): The path to the CSV file.
    """
    with open(file_path, "r") as f:
        if not f.readline():
            logger.warning(f"File is empty: {file_path}")
            return 0
        return sum(1 for _ in f) - 1

def update_custom_metrics(file_path: str):
    """
    Updates the custom metrics for the gathered CSV files.

    Args:
        file_path (str): The path to the CSV file.
    """
    if not os.path.isfile(file_path):
        logger.warning(f"File not found: {file_path}")
    GATHERER_CSV_FILES.set(os.path.getsize(file_path))
    GATHERER_CSV_ROWS.set(_count_csv_rows(file_path))

@app.post(
    "/gather",
    summary="Start traffic gathering",
    description="Gather the traffic into a PCAPG file and two CSV files.",
    response_description="Gathered data.",
    dependencies=[Depends(token_verification_dependency)]
)
@limiter.limit("1/minute")
def gather(request: Request, data: GatheringRequest):
    """
    Starts the traffic gathering process.

    Args:
        request (Request): The FastAPI request object.
        data (GatheringRequest): The request body containing the gathering parameters.
    """
    try:
        result = gather_traffic(data.duration)
        update_custom_metrics(result[-1])
        return {"status": "completed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
