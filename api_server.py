from fastapi import FastAPI, WebSocket
from controller import run_simulation
import asyncio
import json

app = FastAPI(title="AIDRA AI Mission Control API")

@app.get("/mission/start")
async def start_mission():
    # Trigger the simulation and return the final JSON results
    results = run_simulation()
    return results

@app.websocket("/mission/live")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Logic to stream simulation steps one-by-one to the custom UI
    results = run_simulation()
    for log_entry in results['log']:
        await websocket.send_text(json.dumps({"log": log_entry}))
        await asyncio.sleep(0.5) # Simulate real-time delays