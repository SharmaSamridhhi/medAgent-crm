from fastapi import APIRouter

from app.api.v1.hcps import router as hcps_router

api_router = APIRouter()
api_router.include_router(hcps_router)

# Further domain routers (interactions, agent, ...) are included here as
# they land — see MEDGENT-007, MEDGENT-015.
