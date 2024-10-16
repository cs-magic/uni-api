from fastapi import APIRouter

from .rama import rama_router

cases_router = APIRouter(prefix='/cases', tags=['Cases'])

cases_router.include_router(rama_router)