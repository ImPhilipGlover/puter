# /puter/aura/src/persistence/db_client.py
"""
Dedicated module to manage all asynchronous interactions with the ArangoDB
'Living Image'. This client encapsulates all database logic, including the
AQL graph traversal for method resolution, keeping the Orchestrator clean
of persistence-specific code.
"""
import httpx
from typing import Any, Dict, List, Optional, NamedTuple
# RECTIFICATION: Import from the 'arangoasync' library and include 'Auth'.
from arangoasync import ArangoClient
from arangoasync.auth import Auth
from arango.database import StandardDatabase

import src.config as config
from src.core.uvm import UvmObject

class MethodExecutionResult(NamedTuple):
    output: Any
    state_changed: bool
    source_object_id: str

class DbClient:
    """Asynchronous client for interacting with the ArangoDB persistence layer."""

    def __init__(self):
        self.client = ArangoClient(hosts=config.ARANGO_HOST)
        self.db: Optional[StandardDatabase] = None

    async def initialize(self):
        """Initializes the database connection using the Auth object."""
        # RECTIFICATION: Use the 'Auth' class for credentials.
        auth = Auth(
            username=config.ARANGO_USER,
            password=config.ARANGO_PASS
        )
        # RECTIFICATION: Pass the 'auth' object to the db() method.
        self.db = await self.client.db(config.DB_NAME, auth=auth)
        print("Persistence layer (ArangoDB) client initialized.")

    async def shutdown(self):
        """Closes the database connection."""
        # The library's preferred usage is an async context manager,
        # but for a long-lived app, we rely on the process end to close connections.
        print("Persistence layer client shut down.")

    async def get_object(self, object_id: str) -> Optional[UvmObject]:
        """Retrieves and deserializes a UvmObject from the database."""
        if not self.db:
            return None
        uvm_objects = self.db.collection("UvmObjects")
        doc = await uvm_objects.get(object_id)
        return UvmObject.from_doc(doc) if doc else None

    async def install_method(self, target_id: str, method_name: str, code_string: str) -> bool:
        """Atomically installs a new method on a target object."""
        if not self.db:
            return False

        uvm_objects = self.db.collection("UvmObjects")
        # Combine the key and the new method data into one dictionary
        patch_data = {
            '_key': target_id,
            'methods': {method_name: code_string}
        }
        try:
            await uvm_objects.update(patch_data, merge_objects=True)
            return True
        except Exception as e:
            print(f"DBCLIENT ERROR: Failed to install method: {e}")
            return False

    async def resolve_and_execute_method(
        self,
        start_object_id: str,
        method_name: str,
        args: List,
        kwargs: Dict,
        http_client: httpx.AsyncClient
    ) -> Optional[MethodExecutionResult]:
        """
        Resolves a method by traversing the prototype graph and executes it in the sandbox.
        """
        if not self.db:
            return None

        aql_query = """
        FOR v IN 0..100 OUTBOUND @start_node PrototypeLinks
          FILTER HAS(v.methods, @method_name)
          LIMIT 1
          RETURN { obj: v, code: v.methods[@method_name] }
        """
        bind_vars = {
            "start_node": f"UvmObjects/{start_object_id}",
            "method_name": method_name
        }

        cursor = await self.db.aql.execute(aql_query, bind_vars=bind_vars)
        results = [doc async for doc in cursor]

        if not results:
            return None

        # RECTIFICATION: AQL returns a list of results; access the first one.
        found_method = results[0]
        source_object_doc = found_method['obj']
        code_to_execute = found_method['code']

        sandbox_payload = {
            "code": code_to_execute,
            "method_name": method_name,
            "object_state": source_object_doc['attributes'],
            "args": args,
            "kwargs": kwargs
        }

        try:
            response = await http_client.post(config.EXECUTION_SANDBOX_URL, json=sandbox_payload)
            response.raise_for_status()
            result_data = response.json()

            if result_data.get("error"):
                print(f"SANDBOX ERROR: {result_data['error']}")
                return None

            if result_data.get("state_changed", False):
                updated_attributes = result_data.get("final_state", {})
                uvm_objects = self.db.collection("UvmObjects")
                # Combine the key and the new attributes data into one dictionary
                patch_doc = {
                    '_key': source_object_doc['_key'],
                    'attributes': updated_attributes
                }
                await uvm_objects.update(patch_doc)
    
            return MethodExecutionResult(
                output=result_data.get("output"),
                state_changed=result_data.get("state_changed", False),
                source_object_id=source_object_doc['_id']
            )
        except httpx.HTTPStatusError as e:
            print(f"SANDBOX HTTP ERROR: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"SANDBOX EXECUTION ERROR: {e}")
            return None