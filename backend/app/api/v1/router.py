from fastapi import APIRouter

from app.api.v1.hcps import router as hcps_router
from app.api.v1.interactions import router as interactions_router

api_router = APIRouter()
api_router.include_router(hcps_router)
api_router.include_router(interactions_router)

# Further domain routers (agent, ...) are included here as they land —
# see MEDGENT-015.
