from fastapi import FastAPI

app = FastAPI(title="Diagrams AI Service")


@app.get("/health")
def health_check():
    return {"status": "ok"}
