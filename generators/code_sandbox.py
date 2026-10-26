"""
Sandbox Code Validation Engine
Extracts Python code blocks from markdown lessons and executes them in an isolated
subprocess environment with strict timeouts and error isolation.
"""

import ast
import os
import re
import sys
import tempfile
import time
import subprocess
from typing import Dict, List, Any


class CodeSandboxValidator:
    """
    Validates Python code blocks found in generated markdown lessons.
    Ensures imports, math, matrix dimensions, and algorithms run without runtime crashes.
    """

    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds

    def extract_python_blocks(self, markdown_text: str) -> List[str]:
        """
        Extracts all Python code blocks (```python ... ```) from markdown text.
        """
        pattern = r"```(?:python|py)\n(.*?)```"
        blocks = re.findall(pattern, markdown_text, re.DOTALL)
        return [b.strip() for b in blocks if b.strip()]

    def check_syntax(self, code_str: str) -> Dict[str, Any]:
        """
        Validates Python syntax using the AST parser.
        """
        try:
            ast.parse(code_str)
            return {"valid": True, "error": None}
        except SyntaxError as e:
            return {
                "valid": False,
                "error": f"SyntaxError on line {e.lineno}: {e.msg}\nCode snippet: {e.text}"
            }

    def validate_code_blocks(self, markdown_text: str) -> Dict[str, Any]:
        """
        Executes extracted code blocks sequentially in an isolated sandboxed subprocess.
        Automatically applies headless matplotlib backend and captures full stdout/stderr.
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
                "error_details": None
            }

        # Step 1: Pre-execution AST Syntax Check on all blocks
        syntax_errors = []
        for idx, block in enumerate(blocks, 1):
            check = self.check_syntax(block)
            if not check["valid"]:
                syntax_errors.append(f"Block #{idx}: {check['error']}")

        if syntax_errors:
            return {
                "is_valid": False,
                "status_badge": "SYNTAX ERROR",
                "blocks_count": len(blocks),
                "stdout": "",
                "stderr": "\n".join(syntax_errors),
                "execution_time": 0.0,
                "error_details": syntax_errors
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
                    "error_details": f"Subprocess exited with code {result.returncode}.\n{stderr_clean}"
                }

        except subprocess.TimeoutExpired:
            elapsed = round(time.time() - start_time, 2)
            return {
                "is_valid": False,
                "status_badge": f"TIMEOUT EXCEEDED ({self.timeout_seconds}s)",
                "blocks_count": len(blocks),
                "stdout": "",
                "stderr": f"Execution timed out after {self.timeout_seconds} seconds.",
                "execution_time": elapsed,
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
                "error_details": str(ex)
            }
        finally:
            if os.path.exists(temp_script_path):
                try:
                    os.remove(temp_script_path)
                except OSError:
                    pass
