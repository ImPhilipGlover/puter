# /puter/aura/src/config.py
"""
Configuration management for the AURA system.
This module loads environment variables from the.env file and exposes them
as typed constants. This centralizes all configuration parameters, making
the application more secure and easier to configure.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- ArangoDB Configuration ---
ARANGO_HOST = os.getenv("ARANGO_HOST", "http://localhost:8529")
ARANGO_USER = os.getenv("ARANGO_USER", "root")
ARANGO_PASS = os.getenv("ARANGO_PASS")
DB_NAME = os.getenv("DB_NAME", "aura_live_image")

# --- AURA Core Configuration ---
AURA_API_HOST = os.getenv("AURA_API_HOST", "0.0.0.0")
AURA_API_PORT = int(os.getenv("AURA_API_PORT", 8000))

# --- Ollama Configuration ---
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# --- Execution Sandbox Configuration ---
EXECUTION_SANDBOX_URL = os.getenv("EXECUTION_SANDBOX_URL", "http://localhost:8100/execute")

# --- Cognitive Persona Model Mapping ---
# Maps the persona name to the specific Ollama model tag.
# NOTE: The models specified in the original documents have been mapped to the
# models available on the Architect's local machine.
PERSONA_MODELS = {
    "BRICK": "phi4-mini-reasoning:latest",  # Mapped from phi3
    "ROBIN": "gemma3:latest",            # Mapped from llama3
    "BABS": "gemma3:4b",                 # Mapped from gemma:7b
    "ALFRED": "qwen3:4b"                 # Mapped from qwen2:7b
}