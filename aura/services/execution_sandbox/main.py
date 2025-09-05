# /puter/aura/services/execution_sandbox/main.py
import copy
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List

app = FastAPI()

class ExecutionPayload(BaseModel):
    code: str
    method_name: str
    object_state: Dict[str, Any]
    args: List[Any]
    kwargs: Dict[str, Any]

class SandboxObject:
    """A proxy object to safely execute code against."""
    def __init__(self, initial_state: Dict[str, Any]):
        self.attributes = initial_state
        self._p_changed = False

@app.post("/execute")
async def execute_code(payload: ExecutionPayload):
    """
    Executes provided code in a sandboxed environment.
    """
    initial_state = copy.deepcopy(payload.object_state)
    sandbox_self = SandboxObject(initial_state)
    
    # Prepare a local namespace for the exec call
    local_namespace = {'self': sandbox_self}
    
    try:
        # Execute the method definition in the local namespace
        exec(payload.code, {}, local_namespace)
        
        # Get the function object
        method_to_call = local_namespace.get(payload.method_name)
        if not callable(method_to_call):
            raise ValueError(f"Method '{payload.method_name}' not found or not callable after exec.")
            
        # Call the function with the provided arguments
        output = method_to_call(sandbox_self, *payload.args, **payload.kwargs)
        
        return {
            "output": output,
            "state_changed": sandbox_self._p_changed,
            "final_state": sandbox_self.attributes,
            "error": None
        }
    except Exception as e:
        # Return any execution errors in a structured way
        return {
            "output": None,
            "state_changed": False,
            "final_state": payload.object_state,
            "error": f"{type(e).__name__}: {e}"
        }