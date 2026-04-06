from fastapi import FastAPI

app = FastAPI(title="Piano Service", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "piano"}
