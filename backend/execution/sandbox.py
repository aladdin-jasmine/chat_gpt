import subprocess
import tempfile
import os

class SecureSandbox:
    async def execute_python(self, code: str):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tmp:
            tmp.write(code.encode())
            tmp.close()

            result = subprocess.run(
                ['python3', tmp.name],
                capture_output=True,
                text=True,
                timeout=5
            )

            os.unlink(tmp.name)

            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }

    async def execute_bash(self, command: str):
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )

        return {
            'stdout': result.stdout,
            'stderr': result.stderr
        }
