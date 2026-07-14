from fastapi import FastAPI

app = FastAPI(title="medAgent-CRM")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
