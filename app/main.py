from fastapi import FastAPI

app=FastAPI()

@app.get("/")

def home():
    return {"message":"OK"}

@app.get("/health")

def health_check():
    return {"message":"Timeseries service is up and running"}