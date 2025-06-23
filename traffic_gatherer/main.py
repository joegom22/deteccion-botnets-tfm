from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel, Field
from traffic_gatherer.src.gather import gather_traffic
from traffic_gatherer.src.verify import token_verification_dependency

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="IoT Traffic Gathering Service",
    description="""<p> Microservice for network traffic gathering. This service captures network traffic via tcpdump and processes it into a PCAP file. Then it processes the PCAP file to extract flow information combining python algorithm and also tshark and 
    outputs the flow results raw in CSV format and condensed flow data also in CSV format. </p> <p> The resulting 3 files are saved in the shared directory (/app/shared) and can be accessed by other services or users. </p>""",
    version="1.0.0"
)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Request blocked."}
    )

class GatheringRequest(BaseModel):
    duration: int = Field("3600", description="Duration of the traffic gathering (defaults to: 1h)", example=120)

@app.post(
    "/gather",
    summary="Start traffic gathering",
    description="Gather the traffic into a PCAPG file.",
    response_description="Gathered data.",
    dependencies=[Depends(token_verification_dependency)]
)
@limiter.limit("1/minute")
def gather(request: Request, data: GatheringRequest):
    try:
        result = gather_traffic(data.duration)
        return {"status": "completed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
