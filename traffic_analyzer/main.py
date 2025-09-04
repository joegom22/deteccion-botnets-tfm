import os
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse

from pydantic import BaseModel, Field

from src.analyze import analyze_traffic
from src.verify import token_verification_dependency

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Gauge

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="IoT Traffic Analyzing Service",
    summary="Microservice for network traffic analysis.",
    description="""<p> This service analyzes network traffic from a csv file containing flow data. It processes the data to extract insights and makes a prediction of weather a botnet is present in the traffic or not. </p>""",
    version="1.0.0"
)

Instrumentator().instrument(app).expose(app)

app.state.limiter = limiter

ANALYZER_CSV_FILES = Gauge(
    "analyzer_csv_size",
    "Tamaño en bytes del CSV generado por analyze_traffic."
)
ANALYZER_CSV_ROWS = Gauge(
    "analyzer_csv_rows",
    "Número de filas del CSV generado por analyze_traffic."
)

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Request blocked."}
    )

class AnalysisRequest(BaseModel):
    file_path: str = Field(description="File path to the CSV file", example="/app/shared/traffic_data.csv")
    model: str = Field(description="Machine learning model to use", example="XGBoost")

def _count_csv_rows(file_path: str) -> int:
    """
    Counts the number of rows in a CSV file except header.

    Args:
        file_path (str): The path to the CSV file.
    """
    with open(file_path, "r") as f:
        return sum(1 for _ in f) - 1

def update_custom_metrics(file_path: str):
    """
    Updates the custom metrics for the gathered CSV files.

    Args:
        file_path (str): The path to the CSV file.
    """
    ANALYZER_CSV_FILES.set(os.path.getsize(file_path))
    ANALYZER_CSV_ROWS.set(_count_csv_rows(file_path))

@app.post(
    "/analyze",
    summary="Start traffic Analysis",
    description="Analyze the CSV traffic data.",
    response_description="Analysis.",
    dependencies=[Depends(token_verification_dependency)]
)
@limiter.limit("1/minute")
def analyze(request: Request, data: AnalysisRequest):
    """
    Start the traffic analysis process.

    Args:
        request (Request): The FastAPI request object.
        data (AnalysisRequest): The request body containing the analysis parameters.
    """
    try:
        result = analyze_traffic(data.file_path, data.model)
        update_custom_metrics(result["path"])
        return {"status": "completed", "result": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))