from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel, Field
from src.visualize import visualize_analysis
from src.verify import token_verification_dependency

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="IoT Traffic Visualization Service",
    summary="Microservice for network traffic analysis visualization.",
    description="""<p> This service visualizes the analysis results of network traffic from a JSON file. </p>""",
    version="1.0.0"
)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Request blocked."}
    )

class VisualizationRequest(BaseModel):
    file_path: str = Field(description="File path to the CSV file", example="/app/shared/analysis.json")

@app.post(
    "/visualize",
    summary="Start traffic Visualization",
    description="Visualize the JSON analysis data.",
    response_description="Visualization.",
    dependencies=[Depends(token_verification_dependency)]
)
@limiter.limit("1/minute")
def visualize(request: Request, data: VisualizationRequest):
    try:
        result = visualize_analysis(data.file_path)
        return {"status": "completed", "result": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))