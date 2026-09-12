from pathlib import Path
import os
import subprocess
from mcp.server.fastmcp import FastMCP

ROOT = Path(os.environ.get("STUDIO_ROOT", "/workspace")).resolve()
mcp = FastMCP("god-molecule-production-tools")

ALLOWED = {
    "inspect_mars": ["python", "tools/character/inspect_mars_asset.py"],
    "build_oral_bridge": ["python", "tools/character/build_mars_oral_bridge.py"],
    "survey_oral_aperture": ["python", "tools/character/survey_oral_aperture.py"],
}

@mcp.tool()
def list_capabilities() -> dict:
    return {"workspace": str(ROOT), "tools": sorted(ALLOWED)}

@mcp.tool()
def run_character_tool(name: str) -> dict:
    if name not in ALLOWED:
        raise ValueError(f"Tool not allowlisted: {name}")
    result = subprocess.run(
        ALLOWED[name],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=3600,
    )
    return {
        "name": name,
        "returncode": result.returncode,
        "stdout": result.stdout[-12000:],
        "stderr": result.stderr[-12000:],
    }

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
