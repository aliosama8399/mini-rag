from fastapi import FastAPI
# from routes import base, data

app = FastAPI()
@app.get("/welcome")
def welcome():
    return {"message":"hanet"}
    
# app.include_router(base.base_router)
# app.include_router(data.data_router)
