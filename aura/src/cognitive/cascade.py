# /puter/aura/src/cognitive/cascade.py
"""Defines the Entropy Cascade, the system's multi-persona cognitive engine.This module defines the four core personas (BRICK, ROBIN, BABS, ALFRED) andorchestrates their interaction to generate novel and robust outputs. Theinitial implementation pragmatically designates ALFRED as the sole steward forcode generation to ensure stability, an act of 'Structural Empathy'."""
import ollama
from typing import Dict, Any
import src.config as config
from src.cognitive.metacog import MetacognitiveController

class EntropyCascade:
    """Manages the cognitive workflow of the four personas."""
    def __init__(self):
        self.personas = config.PERSONA_MODELS
        self.metacog = MetacognitiveController()
        self.client = None

    async def initialize(self):
        """Initializes the asynchronous Ollama client."""
        self.client = ollama.AsyncClient(host=config.OLLAMA_HOST)
        print("Entropy Cascade initialized.")

    async def generate_code(self, creative_mandate: str, method_name: str) -> str:
        """
        Generates Python code to fulfill a creative mandate.
        For the initial launch, this task is pragmatically delegated solely to
        ALFRED, the most suitable persona for structured code generation.
        """
        if not self.client:
            raise RuntimeError("Ollama client not initialized.")

        # ALFRED is the designated steward for code generation.
        persona_name = "ALFRED"
        model = self.personas.get(persona_name)
        if not model:
            raise ValueError(f"Model for persona '{persona_name}' not found.")

        system_prompt = self.metacog.get_code_generation_prompt(persona_name, method_name)

        print(f"Dispatching code generation task to {persona_name} ({model})...")

        # --- BEGIN LLM LOG ---
        print("\n" + "="*25 + " LLM INPUT " + "="*25)
        print(f"[MODEL]: {model}")
        print(f"[SYSTEM PROMPT]:\n{system_prompt}")
        print(f"\n[USER PROMPT]:\n{creative_mandate}")
        print("="*61 + "\n")
        # ---------------------

        try:
            response = await self.client.chat(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": creative_mandate}
                ],
                format="json"
            )
            
            # --- LLM RAW OUTPUT ---
            print("\n" + "="*23 + " LLM RAW OUTPUT " + "="*23)
            print(response)
            print("="*61 + "\n")
            # ----------------------

            # The metacog module is responsible for parsing the structured response
            code = self.metacog.parse_code_from_response(response)
            return code
        except Exception as e:
            print(f"Error during code generation with {persona_name}: {e}")
            return ""