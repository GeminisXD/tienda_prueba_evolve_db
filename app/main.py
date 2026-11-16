from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import FRONTEND_URL
from app.middleware import TraceIDMiddleware
from app.routers import auth, orders, products

app = FastAPI(title="Tienda Virtual Evolve API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Trace-ID"],
)
app.add_middleware(TraceIDMiddleware)

app.include_router(products.router)
app.include_router(auth.router)
app.include_router(orders.router)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de la Tienda Virtual Evolve"}
