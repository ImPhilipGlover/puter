# /puter/aura/src/core/orchestrator.py
"""
Implements the Orchestrator, the central control unit for the AURA system.
The Orchestrator manages the primary operational loops, including the
'doesNotUnderstand' cycle for first-order autopoiesis. It coordinates
between the persistence layer (DbClient), the cognitive engine
(EntropyCascade), and the security layer (PersistenceGuardian).
"""
import asyncio
import httpx
import ollama
from typing import Any, Dict, List, Optional

from src.persistence.db_client import DbClient, MethodExecutionResult
from src.cognitive.cascade import EntropyCascade
from src.core.security import PersistenceGuardian
import src.config as config

class Orchestrator:
    """Manages the state and control flow of the AURA UVM."""

    def __init__(self):
        self.db_client = DbClient()
        self.cognitive_engine = EntropyCascade()
        self.security_guardian = PersistenceGuardian()
        self.http_client: Optional[httpx.AsyncClient] = None
        self.is_initialized = False

    async def initialize(self):
        """Initializes database connections and other resources."""
        if not self.is_initialized:
            await self.db_client.initialize()
            await self.cognitive_engine.initialize()
            self.http_client = httpx.AsyncClient(timeout=60.0)
            self.is_initialized = True
            print("Orchestrator initialized successfully.")

    async def shutdown(self):
        """Closes connections and cleans up resources."""
        if self.is_initialized:
            await self.db_client.shutdown()
            if self.http_client:
                await self.http_client.aclose()
            self.is_initialized = False
            print("Orchestrator shut down.")
            
    async def check_system_health(self) -> Dict[str, str]:
        """Performs non-blocking checks on system dependencies."""
        health_status = {}
        # Check ArangoDB connection
        try:
            self.db_client.db.version()
            health_status["arangodb"] = "OK"
        except Exception as e:
            health_status["arangodb"] = f"FAIL: {e}"

        # Check Ollama service
        try:
            client = ollama.AsyncClient(host=config.OLLAMA_HOST, timeout=5)
            await client.list()
            health_status["ollama"] = "OK"
        except Exception as e:
            health_status["ollama"] = f"FAIL: {e}"
        return health_status

    async def process_message(self, target_id: str, method_name: str, args: List, kwargs: Dict):
        """
        The main entry point for processing a message.
        If the method is not found, it triggers the 'doesNotUnderstand' autopoietic protocol.
        """
        print(f"Orchestrator: Received message '{method_name}' for target '{target_id}'")
        if not self.http_client:
            raise RuntimeError("HTTP client not initialized.")

        method_result: Optional = await self.db_client.resolve_and_execute_method(
            start_object_id=target_id,
            method_name=method_name,
            args=args,
            kwargs=kwargs,
            http_client=self.http_client
        )

        if method_result is None:
            print(f"Method '{method_name}' not found. Triggering doesNotUnderstand protocol.")
            return await self.does_not_understand(
                target_id=target_id,
                failed_method_name=method_name,
                args=args,
                kwargs=kwargs
            )
        else:
            print(f"Method '{method_name}' executed successfully on '{method_result.source_object_id}'.")
            print(f"Output: {method_result.output}")
            if method_result.state_changed:
                print("Object state was modified and persisted.")
            return {"output": method_result.output, "state_changed": method_result.state_changed}


    async def does_not_understand(self, target_id: str, failed_method_name: str, args: List, kwargs: Dict):
        """
        The core autopoietic loop for generating new capabilities.
        """
        print(f"AUTOPOIESIS: Generating implementation for '{failed_method_name}' on '{target_id}'.")
        creative_mandate = f"Implement method '{failed_method_name}' with args {args} and kwargs {kwargs}"
        generated_code = await self.cognitive_engine.generate_code(creative_mandate, failed_method_name)

        if not generated_code:
            print(f"AUTOFAILURE: Cognitive engine failed to generate code for '{failed_method_name}'.")
            return {"error": "Code generation failed"}

        print(f"AUTOGEN: Generated code for '{failed_method_name}':\n---\n{generated_code}\n---")

        if self.security_guardian.audit(generated_code):
            print("AUDIT: Security audit PASSED.")
            success = await self.db_client.install_method(
                target_id=target_id,
                method_name=failed_method_name,
                code_string=generated_code
            )
            if success:
                print(f"AUTOPOIESIS COMPLETE: Method '{failed_method_name}' installed on '{target_id}'.")
                print("Re-issuing original message...")
                # RECTIFICATION: Re-issuing the message ensures the newly created method
                # is executed via the full, secure `process_message` -> `resolve_and_execute_method`
                # path, which includes the dynamic sandbox validation. This closes the security bypass.
                return await self.process_message(target_id, failed_method_name, args, kwargs)
            else:
                print(f"PERSISTENCE FAILURE: Failed to install method '{failed_method_name}'.")
                return {"error": "Method installation failed"}
        else:
            print(f"AUDIT FAILED: Generated code for '{failed_method_name}' is not secure. Method not installed.")
            return {"error": "Security audit failed"}