from fastapi import APIRouter

from app.routers import auth, billing, health, listings, orders, protected

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(listings.router)
api_router.include_router(orders.router)
api_router.include_router(billing.router)
api_router.include_router(protected.router)
