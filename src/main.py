from fastapi import FastAPI
from src.routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from src.helpers.config import get_settings

app = FastAPI()  
 
@app.lifespan ("startup")
async def startup_db_client():
    settings=get_settings()

    app.mongo_conn= AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client= app.mongo_con[settings.MONGO_DATABASE]

@app.lifespan ("shutdown")
async def shutdown_db_client():
    app.mongo_conn.close()

app.include_router(base.base_router)
app.include_router(data.data_router)
