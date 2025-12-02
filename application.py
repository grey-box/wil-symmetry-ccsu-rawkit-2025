from fastapi import FastAPI
from Operations import operations_router

application:FastAPI = FastAPI()


application.include_router(operations_router)
