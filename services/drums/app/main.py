from fastapi import FastAPI

app = FastAPI(title="Drums Service", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "drums"}
