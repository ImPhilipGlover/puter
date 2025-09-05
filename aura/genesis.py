# /puter/aura/genesis.py
import asyncio
import os
from dotenv import load_dotenv
from arango import ArangoClient
from arango.exceptions import DatabaseCreateError, CollectionCreateError

load_dotenv()

# --- Configuration ---
ARANGO_HOST = os.getenv("ARANGO_HOST")
ARANGO_USER = os.getenv("ARANGO_USER")
ARANGO_PASS = os.getenv("ARANGO_PASS")
DB_NAME = os.getenv("DB_NAME")

async def initialize_database():
    """Connects to ArangoDB and sets up the required database and collections."""
    print("--- Initializing Persistence Layer (ArangoDB) ---")
    try:
        # Use the standard synchronous client for one-off setup scripts.
        client = ArangoClient(hosts=ARANGO_HOST)
        sys_db = client.db("_system", username=ARANGO_USER, password=ARANGO_PASS)

        if not sys_db.has_database(DB_NAME):
            print(f"Creating database: {DB_NAME}")
            sys_db.create_database(DB_NAME)
        else:
            print(f"Database '{DB_NAME}' already exists.")

        db = client.db(DB_NAME, username=ARANGO_USER, password=ARANGO_PASS)

        collections = {
            "UvmObjects": "vertex",
            "PrototypeLinks": "edge",
            "MemoryNodes": "vertex",
            "ContextLinks": "edge"
        }

        for name, col_type in collections.items():
            if not db.has_collection(name):
                print(f"Creating collection: {name}")
                db.create_collection(name, edge=(col_type == "edge"))
            else:
                print(f"Collection '{name}' already exists.")

        uvm_objects = db.collection("UvmObjects")
        if not uvm_objects.has("nil"):
            print("Creating 'nil' root object...")
            nil_obj = {
                "_key": "nil",
                "attributes": {},
                "methods": {}
            }
            uvm_objects.insert(nil_obj)

        if not uvm_objects.has("system"):
            print("Creating 'system' object...")
            system_obj = {
                "_key": "system",
                "attributes": {},
                "methods": {}
            }
            system_doc = uvm_objects.insert(system_obj)

            prototype_links = db.collection("PrototypeLinks")
            if not prototype_links.find({'_from': system_doc['_id'], '_to': 'UvmObjects/nil'}):
                prototype_links.insert({'_from': system_doc['_id'], '_to': 'UvmObjects/nil'})

        print("--- Database initialization complete. ---")
    except Exception as e:
        print(f"An error occurred during database initialization: {e}")
        raise

async def main():
    """Runs the complete genesis protocol."""
    await initialize_database()
    # CLARIFICATION: The build_cognitive_facets function, designed to build fine-tuned LoRA models,
    # is a placeholder for future second-order autopoiesis and is not required for the initial incarnation.
    print("\n--- Genesis Protocol Complete ---")

if __name__ == "__main__":
    asyncio.run(main())