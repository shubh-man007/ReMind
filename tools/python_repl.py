import io
import sys
from .tool import Tool


class PythonREPLTool(Tool):
    def __init__(self):
        super().__init__("python_repl", "Useful for executing Python code.")
        self.locals = {}

    def __call__(self, code_string: str) -> str:
        output_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = output_buffer

        try:
            exec(code_string, {}, self.locals)
        except Exception as e:
            output_buffer.write(f"Error: {e}\n")
        finally:
            sys.stdout = old_stdout

        output = output_buffer.getvalue()
        output_buffer.close()
        return output