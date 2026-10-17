from typing import TypedDict
import os
from langgraph.graph import StateGraph, START, END

class CharacterState(TypedDict, total=False):
    objective: str
    action: str
    result: dict
    approved: bool

ACTIONS = {
    "inspect_mars": ["python", "tools/character/inspect_mars_asset.py"],
    "build_oral_bridge": ["python", "tools/character/build_mars_oral_bridge.py"],
    "survey_oral_aperture": ["python", "tools/character/survey_oral_aperture.py"],
}

def plan(state: CharacterState):
    text = state.get("objective", "").lower()
    if "survey" in text or "aperture" in text:
        action = "survey_oral_aperture"
    elif "oral" in text or "mouth" in text:
        action = "build_oral_bridge"
    else:
        action = "inspect_mars"
    return {"action": action}

def execute(state: CharacterState):
    import subprocess
    action = state["action"]
    p = subprocess.run(ACTIONS[action], cwd=os.environ.get("STUDIO_ROOT", "."),
                       text=True, capture_output=True, timeout=3600)
    return {"result": {"action": action, "returncode": p.returncode,
                       "stdout": p.stdout[-12000:], "stderr": p.stderr[-12000:]}}

def qc(state: CharacterState):
    return {"approved": state["result"]["returncode"] == 0}

graph = StateGraph(CharacterState)
graph.add_node("plan", plan)
graph.add_node("execute", execute)
graph.add_node("qc", qc)
graph.add_edge(START, "plan")
graph.add_edge("plan", "execute")
graph.add_edge("execute", "qc")
graph.add_edge("qc", END)
character_graph = graph.compile()
