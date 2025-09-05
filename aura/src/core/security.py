# /puter/aura/src/core/security.py
"""
Implements the PersistenceGuardian, the system's static security auditor.
This module is a non-negotiable component of the autopoietic loop. It uses
Python's Abstract Syntax Tree (ast) module to inspect all self-generated
code for denylisted patterns before it can be installed into the live system.
This provides a crucial first line of defense against malicious or unstable
code generation.
"""
import ast

class PersistenceGuardian:
    """
    Performs a static AST audit on generated Python code.
    """
    def __init__(self):
        # Denylist of AST node types that are forbidden.
        # This is a conservative list to prevent common vulnerabilities.
        self.denylist = {
            ast.Import,
            ast.ImportFrom,
            # ast.Exec,
            ast.Delete,
        }
        # Denylist of function/attribute names that are forbidden.
        self.name_denylist = {
            'open', 'eval', 'exec', 'exit', 'quit',
            '__import__', 'os', 'sys', 'subprocess', 'shutil', 'socket'
        }

    def audit(self, code_string: str) -> bool:
        """
        Audits a string of Python code for forbidden constructs.
        Returns True if the code is safe, False otherwise.
        """
        try:
            tree = ast.parse(code_string)
            for node in ast.walk(tree):
                if type(node) in self.denylist:
                    print(f"AUDIT FAIL: Forbidden construct found: {type(node).__name__}")
                    return False
                if isinstance(node, ast.Name) and node.id in self.name_denylist:
                    print(f"AUDIT FAIL: Forbidden name used: {node.id}")
                    return False
                if isinstance(node, ast.Attribute) and node.attr in self.name_denylist:
                    print(f"AUDIT FAIL: Forbidden attribute accessed: {node.attr}")
                    return False
            return True
        except SyntaxError as e:
            print(f"AUDIT FAIL: Code contains syntax errors: {e}")
            return False