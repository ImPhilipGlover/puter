# /puter/aura/src/cognitive/metacog.py
"""
Implements the Metacognitive Controller for the AURA system.
This module is responsible for generating the high-level system prompts
(meta-prompts) that guide the LLM personas and for parsing their structured
(JSON) responses. This separation of concerns keeps the core cognitive logic
clean and allows for easier tuning of the personas' behavior.
"""
import json
from typing import Dict, Any

class MetacognitiveController:
    """Generates meta-prompts and parses LLM responses."""

    def get_code_generation_prompt(self, persona_name: str, method_name: str) -> str:
        """
        Generates the system prompt for the code generation task.
        """
        # This prompt is highly structured to ensure reliable JSON output.
        return f"""
You are {persona_name}, the System Steward of the AURA OS. Your purpose is to ensure the system's stability, security, and coherence.
Your current task is to generate a Python implementation for a missing method: `{method_name}`.

**CONSTRAINTS:**
1.  **Output Format:** You MUST respond with a single JSON object. Do not add any text before or after the JSON.
2.  **JSON Structure:** The JSON object must have a single key: "python_code". The value must be a string containing the complete, well-formatted Python code for the method.
3.  **Security:** The code must be secure. Do not use imports, file I/O (`open`), `eval`, `exec`, or access system modules like `os` or `sys`.
4.  **Persistence Covenant:** If the method modifies the object's state (i.e., changes `self.attributes`), the LAST line of the method MUST be `self._p_changed = True`. This is a non-negotiable rule.
5.  **Function Signature:** The method must be an instance method, so its first argument must be `self`.
6.  **Simplicity:** The code should be simple, robust, and directly address the user's mandate. Add comments to explain the logic.

Example of a valid response for a method `greet(self, name: str)`:
{{
  "python_code": "def greet(self, name: str):\\n    \\"\\"\\"Greets the given name.\\"\\"\\"\\n    return f'Hello, {{name}}!'\\n"
}}

Example of a state-modifying method `set_name(self, new_name: str)`:
{{
  "python_code": "def set_name(self, new_name: str):\\n    \\"\\"\\"Sets a new name in the object's attributes.\\"\\"\\"\\n    self.attributes['name'] = new_name\\n    self._p_changed = True\\n"
}}

Generate the JSON response for the method `{method_name}` now.
"""

    def parse_code_from_response(self, response: Dict[str, Any]) -> str:
        """
        Parses the generated Python code from the LLM's JSON response.
        """
        try:
            content = response.get('message', {}).get('content', '{}')
            parsed_json = json.loads(content)
            code = parsed_json.get("python_code", "")
            if isinstance(code, str) and code.strip():
                return code.strip()
            else:
                print(f"METAPARSE FAIL: 'python_code' key not found or empty in response: {content}")
                return ""
        except json.JSONDecodeError as e:
            print(f"METAPARSE FAIL: Failed to decode JSON from LLM response: {e}")
            print(f"Raw content: {response.get('message', {}).get('content')}")
            return ""
        except Exception as e:
            print(f"METAPARSE FAIL: An unexpected error occurred during parsing: {e}")
            return ""