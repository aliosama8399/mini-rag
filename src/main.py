from fastapi import FastAPI
from src.routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from src.helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
app = FastAPI()  
 
async def startup_db_client():
    settings=get_settings()

    app.mongo_conn= AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client= app.mongo_conn[settings.MONGO_DATABASE]

    llm_provider_factory=LLMProviderFactory(settings)

    app.generation_client= llm_provider_factory.create(providers=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)


    app.embedding_client=llm_provider_factory.create(providers=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)


async def shutdown_db_client():
    app.mongo_conn.close()


app.router.lifespan.on_startup.append(startup_db_client)
app.router.lifespan.on_shutdown.append(shutdown_db_client)

app.include_router(base.base_router)
app.include_router(data.data_router)
