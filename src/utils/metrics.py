from prometheus_client import Counter, generate_latest,CONTENT_TYPE_LATEST, Histogram
from fastapi import Request,FastAPI, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

REQUEST_COUNTER = Counter('http_requests_total', 'Total number of HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_latency_seconds', 'HTTP request latency in seconds', ['method', 'endpoint'])

class PrometheusMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        endpoint = request.url.path
        REQUEST_COUNTER.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()

        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)

        return response
    
def setup_metrics(app: FastAPI):

    app.add_middleware(PrometheusMiddleware)

    @app.get("/Tro7532", include_in_schema=False)
    async def metrics():
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    
  