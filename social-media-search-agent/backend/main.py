"""
FastAPI server with WebSocket endpoint.
Runs the LangGraph agent and streams pipeline events to the frontend in real time.
"""
import asyncio
import json
import time
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv

FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"

load_dotenv()

from agent.graph import graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Social Media Search Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def run_agent(user_input: str, event_queue: asyncio.Queue) -> None:
    """Run the LangGraph agent and push events into the queue."""

    async def emit(event_type: str, payload: dict = None):
        await event_queue.put({
            "type": event_type,
            "timestamp": int(time.time() * 1000),
            "payload": payload or {},
        })

    try:
        await graph.ainvoke(
            {"user_input": user_input},
            config={
                "configurable": {"emit": emit},
                "recursion_limit": 25,
            },
        )
    except Exception as exc:
        await event_queue.put({
            "type": "error",
            "timestamp": int(time.time() * 1000),
            "payload": {"message": str(exc)},
        })
    finally:
        # Sentinel so the WebSocket loop knows the agent is done
        await event_queue.put({"type": "__done__", "timestamp": int(time.time() * 1000), "payload": {}})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        # Receive initial query message
        raw = await websocket.receive_text()
        data = json.loads(raw)
        user_input = data.get("query", "").strip()

        if not user_input:
            await websocket.send_json({"type": "error", "payload": {"message": "Empty query."}})
            return

        event_queue: asyncio.Queue = asyncio.Queue()

        # Start agent in background
        agent_task = asyncio.create_task(run_agent(user_input, event_queue))

        # Stream events to client
        while True:
            try:
                event = await asyncio.wait_for(event_queue.get(), timeout=120.0)
            except asyncio.TimeoutError:
                await websocket.send_json({
                    "type": "error",
                    "payload": {"message": "Agent timed out."},
                })
                break

            if event["type"] == "__done__":
                break

            await websocket.send_json(event)

            if event["type"] == "error":
                break

        await agent_task

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await websocket.send_json({
                "type": "error",
                "payload": {"message": str(exc)},
            })
        except Exception:
            pass


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve the built React app for every non-API route."""
    # Try to serve a real file first (JS, CSS, images, etc.)
    candidate = FRONTEND_DIST / full_path
    if candidate.exists() and candidate.is_file():
        return FileResponse(candidate)
    # Fall back to index.html so React Router handles the path
    index = FRONTEND_DIST / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"error": "Frontend not built. Run start.sh to build and start the app."}
