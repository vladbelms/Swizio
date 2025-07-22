import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.responses import Response
from starlette.concurrency import run_in_threadpool
from src.agent import run_agent

app = FastAPI(
    title="Swizio AI Diagram Generator",
    description="An API service to generate diagrams from natural language.",
    version="1.0.0"
)


class DiagramRequest(BaseModel):
    prompt: str


def cleanup_file(path: str):
    """Safely removes a file if it exists."""
    if os.path.exists(path):
        os.remove(path)


@app.post("/diagrams/generate")
async def generate_diagram(request: DiagramRequest):
    """
    Receives a user prompt and generates a diagram by running the agent
    in a separate thread to prevent blocking the main event loop.
    """
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    try:
        image_path = await run_in_threadpool(run_agent, request.prompt)
        if not image_path or not os.path.exists(image_path):
            print(f"Error: Agent returned an invalid path: '{image_path}'")
            raise HTTPException(status_code=500, detail="Agent failed to generate a valid diagram file.")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        cleanup_file(image_path)

        return Response(content=image_bytes, media_type="image/png")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")


@app.get("/health")
def health_check():
    """A simple health check endpoint."""
    return {"status": "ok"}
