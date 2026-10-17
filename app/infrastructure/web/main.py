from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import DomainError, InvalidOrderState, OrderNotFound
from app.infrastructure.web.routers import kds_dashboard, webhooks

app = FastAPI(title="Restaurant Automation")


@app.get("/health")
def health():
    return {"status": "ok"}


# أخطاء الـ domain بتتحول لأكواد HTTP هنا (الـ domain نفسه ميعرفش حاجة عن HTTP)
@app.exception_handler(OrderNotFound)
async def order_not_found_handler(request: Request, exc: OrderNotFound):
    return JSONResponse(status_code=404, content={"detail": f"order not found: {exc}"})


@app.exception_handler(InvalidOrderState)
async def invalid_state_handler(request: Request, exc: InvalidOrderState):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


app.include_router(webhooks.router)
app.include_router(kds_dashboard.router)
