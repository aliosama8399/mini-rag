from fastapi import FastAPI
from src.routes import base, data

app = FastAPI()
# @app.get("/")
# def welcome():
#     return {"message":"hanet"}
    
app.include_router(base.base_router)
app.include_router(data.data_router)
