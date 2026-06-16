import httpx
from fastapi.responses import JSONResponse

async def forward_request(
    method: str, 
    url: str, 
    payload: dict = None, 
    timeout: float = 3.0
):
    """
    Proxies the request to an internal service. Acts as a circuit breaker
    if the service is unreachable or times out.
    """
    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, timeout=timeout)
            elif method.upper() == "POST":
                response = await client.post(url, json=payload, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Forward the exact JSON and HTTP status code from the internal service
            return JSONResponse(status_code=response.status_code, content=response.json())
            
        except httpx.TimeoutException:
            # Circuit Breaker: Timeout triggered
            return JSONResponse(
                status_code=504,
                content={
                    "success": False,
                    "error": {
                        "code": "GATEWAY_TIMEOUT",
                        "message": "Oops! The service is taking a bit too long to respond. Please try again later."
                    }
                }
            )
            
        except httpx.RequestError:
            # Circuit Breaker: Connection Refused / Service Offline
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "error": {
                        "code": "SERVICE_UNAVAILABLE",
                        "message": "Oops! This service is currently down or unreachable. We are looking into it."
                    }
                }
            )