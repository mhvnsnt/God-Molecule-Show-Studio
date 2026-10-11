#!/usr/bin/env python3
"""Knowledge graph query interface — TRIPPEDD show canon (Oct 2026).

Usage:
    python3 kg.py "who is Cipher"
    python3 kg.py "what is the relationship between Static and Ashes"
    python3 kg.py "what episodes exist"
    python3 kg.py "who voices Sombra Negra"
    python3 kg.py "list characters"
    python3 kg.py contradictions
    python3 kg.py search "pier"

Facts come only from ~/workspace/tools/brain/knowledge-graph/graph.json.
Never invents canon: unknown values are reported as UNKNOWN/TBD.
"""

import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
GRAPH_PATH = os.path.join(BASE, "graph.json")

try:
    with open(GRAPH_PATH) as f:
        graph = json.load(f)
except FileNotFoundError:
    sys.exit(f"graph.json not found at {GRAPH_PATH}")

nodes = graph.get("nodes", {})
edges = graph.get("edges", [])
contradictions = graph.get("contradictions", [])


# ---------------------------------------------------------------- index helpers

def build_index():
    """Lowercased name/alias/id -> node id, longest keys first."""
    index = {}
    for nid, n in nodes.items():
        keys = [nid.replace("_", " "), n.get("name", "").lower()] + \
               [a.lower() for a in n.get("aliases", [])]
        for k in keys:
            if k and k not in index:
                index[k] = nid
    return dict(sorted(index.items(), key=lambda kv: -len(kv[0])))


INDEX = build_index()


def find_nodes(query):
    """Return node ids mentioned in the query, longest match wins per span."""
    q = " " + query.lower() + " "
    found, covered = [], []
    for key, nid in INDEX.items():
        pat = " " + key + " "
        if pat in q and not any(pat.strip() in c for c in covered):
            found.append(nid)
            covered.append(pat.strip())
    return found


def incoming(nid):
    return [e for e in edges if e.get("to") == nid]


def outgoing(nid):
    return [e for e in edges if e.get("from") == nid]


def node_label(nid):
    n = nodes.get(nid, {})
    return f"{n.get('name', nid)} ({n.get('type', '?')})"


# ---------------------------------------------------------------- formatters

def fmt_value(v):
    if isinstance(v, list):
        return "; ".join(str(x) for x in v)
    return str(v)


def profile(nid):
    n = nodes[nid]
    lines = [f"## {n['name']} [{n.get('type', '?')}]"]
    if n.get("aliases"):
        lines.append(f"Aliases: {', '.join(n['aliases'])}")
    if n.get("description"):
        lines.append(f"\n{n['description']}")
    for key, val in (n.get("props") or {}).items():
        lines.append(f"\n  {key}: {fmt_value(val)}")
    ins, outs = incoming(nid), outgoing(nid)
    if outs or ins:
        lines.append("\nRelationships:")
        for e in outs:
            note = f" — {e['note']}" if e.get("note") else ""
            lines.append(f"  {n['name']}  --{e['rel']}-->  {node_label(e['to'])}{note}")
        for e in ins:
            note = f" — {e['note']}" if e.get("note") else ""
            lines.append(f"  {node_label(e['from'])}  --{e['rel']}-->  {n['name']}{note}")
    if n.get("sources"):
        lines.append("\nSources:")
        for s in n["sources"]:
            lines.append(f"  - {s}")
    return "\n".join(lines)


def relationship(a_id, b_id):
    a, b = nodes[a_id], nodes[b_id]
    lines = [f"## Relationship: {a['name']} ↔ {b['name']}"]
    direct = [e for e in edges
              if (e.get("from") == a_id and e.get("to") == b_id) or
                 (e.get("from") == b_id and e.get("to") == a_id)]
    if direct:
        lines.append("\nDirect links:")
        for e in direct:
            note = f" — {e['note']}" if e.get("note") else ""
            src = f" [src: {e['source']}]" if e.get("source") else ""
            lines.append(f"  {node_label(e['from'])} --{e['rel']}--> {node_label(e['to'])}{note}{src}")
    # 2-hop via shared node
    a_neighbors = {e.get("to") for e in outgoing(a_id)} | {e.get("from") for e in incoming(a_id)}
    b_neighbors = {e.get("to") for e in outgoing(b_id)} | {e.get("from") for e in incoming(b_id)}
    shared = (a_neighbors & b_neighbors) - {a_id, b_id}
    shared.discard("")
    if shared:
        lines.append("\nConnected through:")
        for mid in sorted(shared):
            lines.append(f"  {a['name']} ↔ {node_label(mid)} ↔ {b['name']}")
    if not direct and not shared:
        lines.append("\nNo relationship recorded in canon sources.")
    return "\n".join(lines)


def list_type(ntype):
    hits = [(nid, n) for nid, n in nodes.items() if n.get("type") == ntype]
    if not hits:
        return f"No nodes of type '{ntype}' in the graph."
    lines = [f"## {ntype.title()}s ({len(hits)})"]
    for nid, n in sorted(hits, key=lambda x: x[1]["name"]):
        desc = n.get("description", "")[:120]
        lines.append(f"- {n['name']}: {desc}")
    return "\n".join(lines)


def list_contradictions():
    if not contradictions:
        return "No contradictions flagged."
    lines = [f"## Flagged contradictions / open questions ({len(contradictions)})"]
    for c in contradictions:
        lines.append(f"\n[{c['id']}] {c['topic']}")
        lines.append(f"  status: {c.get('status', '?')}")
        lines.append(f"  {c['detail']}")
        for s in c.get("sources", []):
            lines.append(f"  src: {s}")
    return "\n".join(lines)


# ---------------------------------------------------------------- intents

LIST_TYPES = {"character": "character", "characters": "character",
              "episode": "episode", "episodes": "episode",
              "show": "show", "shows": "show",
              "person": "person", "people": "person",
              "place": "place", "places": "place",
              "concept": "concept", "concepts": "concept",
              "role": "role", "roles": "role"}


def answer(query):
    q = query.strip()
    ql = q.lower()

    if re.search(r"contradiction|open question|disagree|conflict", ql):
        return list_contradictions()

    m = re.search(r"relationship between (.+)", ql)
    if not m:
        m = re.search(r"relationship of (.+)", ql)
    if m:
        rest = m.group(1)
        parts = re.split(r"\s+(?:and|with|vs\.?|to)\s+", rest, maxsplit=1)
        if len(parts) == 2:
            a = find_nodes(parts[0])
            b = find_nodes(parts[1])
            if a and b:
                return relationship(a[0], b[0])
        return "Could not identify two entities in: " + rest

    for key, ntype in LIST_TYPES.items():
        if re.match(rf"^(list|show me|what|which)\b.*\b{key}\b", ql) or \
           re.match(rf"^(list|show me) {key}$", ql):
            return list_type(ntype)
        if ql in (f"what {key} exist", f"which {key} exist", f"what {key} are there",
                   "what episodes exist", "what shows exist"):
            return list_type(ntype)

    if re.search(r"who voices|voiced by|voice of|who does the voice", ql):
        hits = find_nodes(q)
        out = []
        for nid in hits:
            for e in edges:
                if e.get("rel") in ("voiced_by",) and e.get("from") == nid:
                    p = nodes.get(e["to"], {})
                    out.append(f"{nodes[nid]['name']} is voiced by {p.get('name', e['to'])}"
                               f" — {(e.get('note') or '').strip()}")
        if out:
            return "## Voice credits\n" + "\n".join(f"- {x}" for x in out)
        return "No voice credit recorded in canon sources."

    if re.search(r"based on\b|based_on", ql):
        hits = find_nodes(q)
        out = []
        for nid in hits:
            for e in edges:
                if e.get("rel") == "based_on" and e.get("from") == nid:
                    p = nodes.get(e["to"], {})
                    out.append(f"{nodes[nid]['name']} is based on {p.get('name', e['to'])}"
                               f" — {(e.get('note') or '').strip()}")
        if out:
            return "## Based-on relationships\n" + "\n".join(f"- {x}" for x in out)
        return "No based-on relationship recorded in canon sources."

    if re.search(r"robe color|robe colour|robe of|what robe", ql):
        hits = find_nodes(q)
        out = []
        for nid in hits:
            robe = (nodes[nid].get("props") or {}).get("robe")
            if robe:
                out.append(f"{nodes[nid]['name']}: {robe}")
        if out:
            return "## Robe colors\n" + "\n".join(f"- {x}" for x in out)
        return "No robe color recorded in canon sources."

    if ql.startswith("search "):
        term = q[7:].lower()
        hits = [nid for nid, n in nodes.items()
                if term in n.get("name", "").lower()
                or term in n.get("description", "").lower()
                or term in " ".join(n.get("aliases", [])).lower()]
        if not hits:
            return f"No matches for '{q[7:]}'."
        lines = [f"## Search: '{q[7:]}' ({len(hits)})"]
        for nid in hits:
            lines.append(f"- {node_label(nid)}")
        return "\n".join(lines)

    hits = find_nodes(q)
    if hits:
        return "\n\n---\n\n".join(profile(nid) for nid in hits)

    return ("I couldn't match that to any canon entity. Try: "
            "'who is Cipher', 'list characters', 'what episodes exist', "
            "'relationship between Static and Ashes', 'who voices Sombra Negra', "
            "'robe color of Echo', 'search pier', or 'contradictions'.")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    print(answer(" ".join(sys.argv[1:])))


if __name__ == "__main__":
    main()
