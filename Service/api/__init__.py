from fastapi import FastAPI
from .app import router as insurance_router

def create_app():
    app = FastAPI()
    return app

base_api_route = "/algorithm/api"


def register_routes(app: FastAPI):
    """
    init all routers
    """
    # eeg router
    app.include_router(insurance_router, prefix=base_api_route)
  