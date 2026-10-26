"""
Sandbox Code Validation Engine
Extracts Python code blocks from markdown lessons and executes them in an isolated
subprocess environment with strict timeouts, AST security filtering, and error isolation.
"""

import ast
import os
import re
import sys
import tempfile
import time
import subprocess
from typing import Dict, List, Any


class SecurityASTValidator(ast.NodeVisitor):
    """
    Scans the AST of extracted code blocks for potentially destructive, dangerous,
    or unauthorized system operations before subprocess execution.
    """

    BLOCKED_MODULES = {"shutil", "socket", "ctypes", "winreg"}
    BLOCKED_CALLS = {
        "os.system",
        "os.popen",
        "os.remove",
        "os.unlink",
        "os.rmdir",
        "shutil.rmtree",
        "subprocess.Popen",
        "subprocess.call",
        "subprocess.run",
        "sys.exit",
        "eval",
        "exec",
        "__import__"
    }

    def __init__(self):
        self.violations: List[str] = []

    def _get_call_name(self, node: ast.AST) -> str:
        """Resolves compound function call names (e.g. os.system)."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value_name = self._get_call_name(node.value)
            return f"{value_name}.{node.attr}" if value_name else node.attr
        return ""

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            root_module = alias.name.split(".")[0]
            if root_module in self.BLOCKED_MODULES:
                self.violations.append(f"Blocked module import: '{alias.name}' at line {node.lineno}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            root_module = node.module.split(".")[0]
            if root_module in self.BLOCKED_MODULES:
                self.violations.append(f"Blocked 'from {node.module} import ...' at line {node.lineno}")
        for alias in node.names:
            if alias.name in ["rmtree", "system", "Popen"]:
                self.violations.append(f"Blocked imported function: '{alias.name}' at line {node.lineno}")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        call_name = self._get_call_name(node.func)
        if call_name in self.BLOCKED_CALLS:
            self.violations.append(f"Prohibited call: '{call_name}()' at line {node.lineno}")
        self.generic_visit(node)


class CodeSandboxValidator:
    """
    Validates Python code blocks found in generated markdown lessons.
    Ensures imports, math, matrix dimensions, and algorithms run safely without runtime crashes.
    """

    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds

    def extract_python_blocks(self, markdown_text: str) -> List[str]:
        """
        Extracts all Python code blocks (```python ... ```) from markdown text.
        """
        pattern = r"```(?:python|py)[ \t]*\r?\n(.*?)```"
        blocks = re.findall(pattern, markdown_text, re.DOTALL | re.IGNORECASE)
        return [b.strip() for b in blocks if b.strip()]

    def check_syntax_and_security(self, code_str: str) -> Dict[str, Any]:
        """
        Validates Python syntax and enforces AST security rules against destructive calls.
        """
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return {
                "valid": False,
                "error": f"SyntaxError on line {e.lineno}: {e.msg}\nCode snippet: {e.text}"
            }

        # Perform AST security audit
        validator = SecurityASTValidator()
        validator.visit(tree)
        if validator.violations:
            return {
                "valid": False,
                "error": "SecurityViolation: " + "; ".join(validator.violations)
            }

        return {"valid": True, "error": None}

    def validate_code_blocks(self, markdown_text: str) -> Dict[str, Any]:
        """
        Executes extracted code blocks sequentially in an isolated sandboxed subprocess.
        Automatically applies headless matplotlib backend and captures full stdout/stderr.
        Outputs structured telemetry.
        """
        blocks = self.extract_python_blocks(markdown_text)

        if not blocks:
            return {
                "is_valid": True,
                "status_badge": "VERIFIED (No code blocks)",
                "blocks_count": 0,
                "stdout": "No executable code blocks detected.",
                "stderr": "",
                "execution_time": 0.0,
                "execution_time_sec": 0.0,
                "exit_code": 0,
                "output": "No executable code blocks detected.",
                "error": "",
                "error_details": None
            }

        # Step 1: Pre-execution AST Syntax & Security Check on all blocks
        security_and_syntax_errors = []
        for idx, block in enumerate(blocks, 1):
            check = self.check_syntax_and_security(block)
            if not check["valid"]:
                security_and_syntax_errors.append(f"Block #{idx}: {check['error']}")

        if security_and_syntax_errors:
            err_msg = "\n".join(security_and_syntax_errors)
            badge = "SECURITY VIOLATION" if "SecurityViolation" in err_msg else "SYNTAX ERROR"
            return {
                "is_valid": False,
                "status_badge": badge,
                "blocks_count": len(blocks),
                "stdout": "",
                "stderr": err_msg,
                "execution_time": 0.0,
                "execution_time_sec": 0.0,
                "exit_code": 1,
                "output": "",
                "error": err_msg,
                "error_details": security_and_syntax_errors
            }

        # Step 2: Assemble executable script
        # Inject non-interactive matplotlib backend and seed for reproducible verification
        script_preamble = (
            "import sys\n"
            "import os\n"
            "try:\n"
            "    import matplotlib\n"
            "    matplotlib.use('Agg')\n"
            "except ImportError:\n"
            "    pass\n\n"
            "import numpy as np\n"
            "np.random.seed(42)\n\n"
        )

        full_script = script_preamble + "\n\n# --- LESSON CODE BLOCKS ---\n"
        for i, block in enumerate(blocks, 1):
            full_script += f"\n# [Block {i}]\n" + block + "\n"

        # Step 3: Run inside isolated temp file subprocess
        start_time = time.time()
        temp_dir = tempfile.gettempdir()
        temp_script_path = os.path.join(temp_dir, f"sandbox_verify_{int(time.time() * 1000)}.py")

        try:
            with open(temp_script_path, "w", encoding="utf-8") as f:
                f.write(full_script)

            # Subprocess execution with strict timeout
            result = subprocess.run(
                [sys.executable, temp_script_path],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                env={**os.environ, "PYTHONWARNINGS": "ignore"}
            )
            elapsed = round(time.time() - start_time, 2)

            if result.returncode == 0:
                stdout_clean = result.stdout.strip()
                return {
                    "is_valid": True,
                    "status_badge": "VERIFIED (0 errors)",
                    "blocks_count": len(blocks),
                    "stdout": stdout_clean or "Executed successfully with exit code 0.",
                    "stderr": result.stderr.strip(),
                    "execution_time": elapsed,
                    "execution_time_sec": elapsed,
                    "exit_code": 0,
                    "output": stdout_clean or "Executed successfully with exit code 0.",
                    "error": "",
                    "error_details": None
                }
            else:
                stderr_clean = result.stderr.strip()
                return {
                    "is_valid": False,
                    "status_badge": "RUNTIME ERROR",
                    "blocks_count": len(blocks),
                    "stdout": result.stdout.strip(),
                    "stderr": stderr_clean,
                    "execution_time": elapsed,
                    "execution_time_sec": elapsed,
                    "exit_code": result.returncode,
                    "output": result.stdout.strip(),
                    "error": stderr_clean,
                    "error_details": f"Subprocess exited with code {result.returncode}.\n{stderr_clean}"
                }

        except subprocess.TimeoutExpired:
            elapsed = round(time.time() - start_time, 2)
            timeout_msg = f"Execution timed out after {self.timeout_seconds} seconds."
            return {
                "is_valid": False,
                "status_badge": f"TIMEOUT EXCEEDED ({self.timeout_seconds}s)",
                "blocks_count": len(blocks),
                "stdout": "",
                "stderr": timeout_msg,
                "execution_time": elapsed,
                "execution_time_sec": elapsed,
                "exit_code": 124,
                "output": "",
                "error": timeout_msg,
                "error_details": f"Execution exceeded safety limit of {self.timeout_seconds}s."
            }
        except Exception as ex:
            elapsed = round(time.time() - start_time, 2)
            return {
                "is_valid": False,
                "status_badge": "EXECUTION FAILED",
                "blocks_count": len(blocks),
                "stdout": "",
                "stderr": str(ex),
                "execution_time": elapsed,
                "execution_time_sec": elapsed,
                "exit_code": 1,
                "output": "",
                "error": str(ex),
                "error_details": str(ex)
            }
        finally:
            if os.path.exists(temp_script_path):
                try:
                    os.remove(temp_script_path)
                except OSError:
                    pass
