# /puter/aura/src/core/uvm.py
"""
Implements the Universal Virtual Machine's core object model.
This module defines the UvmObject, the foundational building block of the AURA
system. It realizes the prototype-based, message-passing paradigm inspired by
the Self and Smalltalk programming languages. The __getattr__ method is the heart
of the prototypal delegation. When this traversal fails, it is the sole
trigger for the 'doesNotUnderstand' protocol, the system's mechanism for
first-order autopoiesis.
"""
from typing import Any, Dict, Optional

class UvmObject:
    """The universal prototype object for the AURA system."""

    def __init__(self,
                 doc_id: Optional[str] = None,
                 key: Optional[str] = None,
                 attributes: Optional[Dict[str, Any]] = None,
                 methods: Optional[Dict[str, str]] = None):
        self._id = doc_id
        self._key = key
        self.attributes = attributes if attributes is not None else {}
        self.methods = methods if methods is not None else {}
        # This flag is the subject of the "Persistence Covenant".
        self._p_changed = False

    def __getattr__(self, name: str) -> Any:
        """
        Implements the core logic for prototypal delegation.
        This is a placeholder; the actual traversal is managed by the DbClient.
        If the DbClient traversal returns nothing, the Orchestrator will raise
        the final AttributeError that triggers the doesNotUnderstand protocol.
        """
        if name in self.attributes:
            return self.attributes[name]
        if name in self.methods:
            # This is a placeholder. Actual execution is handled by the Orchestrator.
            def method_placeholder(*args, **kwargs):
                pass
            return method_placeholder
        raise AttributeError(
            f"'{type(self).__name__}' object with id '{self._id}' has no "
            f"attribute '{name}'. This signals a 'doesNotUnderstand' event."
        )

    def __setattr__(self, name: str, value: Any):
        """Overrides attribute setting to manage state changes correctly."""
        if name.startswith('_') or name in ['attributes', 'methods']:
            super().__setattr__(name, value)
        else:
            self.attributes[name] = value
            self._p_changed = True

    def to_doc(self) -> Dict[str, Any]:
        """Serializes the UvmObject into a dictionary for ArangoDB storage."""
        doc = {
            'attributes': self.attributes,
            'methods': self.methods
        }
        if self._key:
            doc['_key'] = self._key
        return doc

    @staticmethod
    def from_doc(doc: Dict[str, Any]) -> 'UvmObject':
        """Deserializes a dictionary from ArangoDB into a UvmObject instance."""
        return UvmObject(
            doc_id=doc.get('_id'),
            key=doc.get('_key'),
            attributes=doc.get('attributes', {}),
            methods=doc.get('methods', {})
        )