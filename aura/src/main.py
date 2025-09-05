# /puter/aura/src/main.py
"""
Main application entry point for the AURA system.
This script initializes and runs the FastAPI web server, which serves as the
primary API Gateway for all external interactions with the AURA UVM.
"""
import uvicorn
import asyncio
from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel, Field
from typing import Dict, Any, List
import json

import src.config as config
from src.core.orchestrator import Orchestrator

app = FastAPI(
    title="AURA (Autopoietic Universal Reflective Architecture)",
    description="API Gateway for the AURA Universal Virtual Machine.",
    version="1.0.0"
)

orchestrator = Orchestrator()

@app.on_event("startup")
async def startup_event():
    """Application startup event handler."""
    await orchestrator.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler."""
    await orchestrator.shutdown()

class MessagePayload(BaseModel):
    """Defines the structure for an incoming message to the UVM."""
    target_object_id: str = Field(..., description="The _key of the target UvmObject (e.g., 'system').")
    method_name: str = Field(..., description="The name of the method to invoke.")
    args: List[Any] = Field(default_factory=list, description="Positional arguments for the method.")
    kwargs: Dict[str, Any] = Field(default_factory=dict, description="Keyword arguments for the method.")

@app.post("/message")
async def send_message_to_uvm(payload: MessagePayload):
    """
    Sends a message to a UvmObject, potentially triggering autopoiesis.
    """
    try:
        result = await orchestrator.process_message(
            target_id=payload.target_object_id,
            method_name=payload.method_name,
            args=payload.args,
            kwargs=payload.kwargs
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e}"
        )

@app.get("/health")
async def get_system_health():
    """
    Provides a health check of the AURA system and its dependencies.
    This is a non-negotiable endpoint for stability and monitorability.
    """
    health = await orchestrator.check_system_health()
    is_healthy = all(status == "OK" for status in health.values())
    status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    return Response(content=json.dumps(health), status_code=status_code, media_type="application/json")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.AURA_API_HOST,
        port=config.AURA_API_PORT,
        reload=True
    )