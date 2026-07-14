from fastapi import APIRouter

from app.api.v1.agent import router as agent_router
from app.api.v1.follow_ups import router as follow_ups_router
from app.api.v1.hcps import router as hcps_router
from app.api.v1.interactions import router as interactions_router

api_router = APIRouter()
api_router.include_router(hcps_router)
api_router.include_router(interactions_router)
api_router.include_router(follow_ups_router)
api_router.include_router(agent_router)
