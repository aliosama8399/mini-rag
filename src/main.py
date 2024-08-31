from fastapi import FastAPI
import uvicorn
from routes import base, data,nlp
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
app = FastAPI()  
 
@app.on_event("startup")

async def startup_span():
    settings=get_settings()

    app.mongo_conn= AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client= app.mongo_conn[settings.MONGO_DATABASE]

    llm_provider_factory=LLMProviderFactory(settings)
    vectordb_provider_factory=VectorDBProviderFactory(settings)

    app.generation_client= llm_provider_factory.create(providers=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)


    app.embedding_client=llm_provider_factory.create(providers=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)


    app.vectordb_client = vectordb_provider_factory.create(
        providers= settings.VECTOR_DB_BACKEND
    )
    app.vectordb_client.connect()
@app.on_event("shutdown")

async def shutdown_span():
    app.mongo_conn.close()
    app.vectordb_client.disconnect()


# app.router.lifespan.on_startup.append(startup_span)
# app.router.lifespan_context(startup_span)
# app.router.lifespan.on_shutdown.append(shutdown_span)
# app.router.lifespan_context(shutdown_span)
app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
# if __name__ == '__main__':
#     uvicorn.run(app,  port=8000)