from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel, Field
from src.analyze import analyze_traffic
from src.verify import token_verification_dependency

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from prometheus_fastapi_instrumentator import Instrumentator

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="IoT Traffic Analyzing Service",
    summary="Microservice for network traffic analysis.",
    description="""<p> This service analyzes network traffic from a csv file containing flow data. It processes the data to extract insights and makes a prediction of weather a botnet is present in the traffic or not. </p>""",
    version="1.0.0"
)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Request blocked."}
    )

class AnalysisRequest(BaseModel):
    file_path: str = Field(description="File path to the CSV file", example="/app/shared/traffic_data.csv")

@app.post(
    "/analyze",
    summary="Start traffic Analysis",
    description="Analyze the CSV traffic data.",
    response_description="Analysis.",
    dependencies=[Depends(token_verification_dependency)]
)
@limiter.limit("1/minute")
def analyze(request: Request, data: AnalysisRequest):
    try:
        result = analyze_traffic(data.file_path)
        return {"status": "completed", "result": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

Instrumentator().instrument(app).expose(app)
