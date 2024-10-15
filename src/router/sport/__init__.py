from fastapi import APIRouter

from .badminton import badminton_router
sport_router = APIRouter(prefix='/sport')

sport_router.include_router(badminton_router)