"""Simple frontend server"""
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Recommendation System Frontend")

# Serve static files
frontend_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
async def index():
    """Serve the main index.html"""
    return FileResponse(frontend_dir / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
