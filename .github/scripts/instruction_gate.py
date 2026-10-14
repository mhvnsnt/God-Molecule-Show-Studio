#!/usr/bin/env python3
"""Instruction gate: fails a PR whose body does not prove the owner's method was followed.

Usage in CI:  python3 .github/scripts/instruction_gate.py   (reads GITHUB_EVENT_PATH)
Library use:  check(body, changed_files, repo_root, labels, author) -> list of errors
"""
import json
import os
import re
import subprocess
import sys

SECTIONS = [
    ("instruction", "Owner instruction (verbatim quote)"),
    ("specified", "Method the owner specified"),
    ("used", "Method actually used"),
    ("deviations", "Deviations (none / list, each with owner approval link)"),
    ("proof", "Proof (paths to files, frames, test output)"),
    ("selfcheck", "Self-check: I verified the result against the literal instruction"),
]
PLACEHOLDER = re.compile(r"^>\s*Paste the owner's exact words\. Do not paraphrase\.$", re.I)
APPROVAL_REF = re.compile(r"(https?://\S+|#\d+)")
NONE_WORDS = {"none", "none.", "n/a", "no deviations", "no deviations."}


def _norm_heading(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def parse_sections(body):
    """Return {key: text} for the required sections (comments stripped)."""
    body = re.sub(r"<!--.*?-->", "", body or "", flags=re.S)
    wanted = {_norm_heading(title): key for key, title in SECTIONS}
    out, cur = {}, None
    for line in body.splitlines():
        m = re.match(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$", line)
        if m:
            h = _norm_heading(m.group(1))
            cur = next((k for t, k in wanted.items() if h == t or h.startswith(t)), None)
            if cur is not None:
                out.setdefault(cur, [])
            continue
        if cur is not None:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def _norm_method(s):
    s = re.sub(r"[`*_>\-]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip(" .")


def extract_paths(proof):
    paths = re.findall(r"`([^`\s]+)`", proof)
    if not paths:
        for line in proof.splitlines():
            line = re.sub(r"^\s*[-*+]\s+", "", line).strip()
            if line and " " not in line:
                paths.append(line)
    return [p.strip().lstrip("./") if p.startswith("./") else p.strip() for p in paths]


def _exists(repo_root, p):
    if os.path.exists(os.path.join(repo_root, p)):
        return True
    # sparse checkout in CI: ask git whether the path exists at HEAD
    r = subprocess.run(["git", "-C", repo_root, "cat-file", "-e", f"HEAD:{p}"],
                       capture_output=True)
    return r.returncode == 0


def check(body, changed_files, repo_root=".", labels=(), author=""):
    labels = {l.lower() for l in labels}
    if author.lower() in {"dependabot[bot]", "dependabot"}:
        return []
    if "docs-only" in labels:
        non_md = [f for f in changed_files if not f.lower().endswith(".md")]
        if not non_md:
            return []
        return ["'docs-only' label is set but the PR changes non-.md files: " + ", ".join(non_md[:10])]

    errors = []
    sec = parse_sections(body)
    for key, title in SECTIONS:
        text = sec.get(key)
        if text is None:
            errors.append(f"Missing required section: '## {title}'")
        elif not text or (key == "instruction" and PLACEHOLDER.match(text)):
            errors.append(f"Section is empty: '## {title}'")
    if errors:
        return errors

    dev = sec["deviations"]
    dev_is_none = _norm_method(dev) in {_norm_method(w) for w in NONE_WORDS}
    if _norm_method(sec["specified"]) != _norm_method(sec["used"]) and dev_is_none:
        errors.append("'Method actually used' differs from 'Method the owner specified' but Deviations says none. "
                      "Use the method he named, or list the deviation with his approval link.")
    if not dev_is_none:
        items = [l for l in dev.splitlines() if l.strip()]
        for item in items:
            if not APPROVAL_REF.search(item):
                errors.append(f"Deviation has no owner approval link/#ref: {item.strip()}")

    paths = extract_paths(sec["proof"])
    if not paths:
        errors.append("Proof lists no paths. Put each file/frame/test-output path in backticks.")
    changed = set(changed_files)
    for p in paths:
        if p not in changed and not _exists(repo_root, p):
            errors.append(f"Proof path not in this PR's diff or the repo: {p}")

    if not re.search(r"^\s*[-*]\s+\[[xX]\]", sec["selfcheck"], re.M):
        errors.append("Self-check box is not ticked ([x]).")
    return errors


def main():
    with open(os.environ["GITHUB_EVENT_PATH"]) as f:
        ev = json.load(f)
    pr = ev["pull_request"]
    repo = ev["repository"]["full_name"]
    files = subprocess.run(["gh", "api", "--paginate", f"repos/{repo}/pulls/{pr['number']}/files",
                            "-q", ".[].filename"],
                           capture_output=True, text=True, check=True).stdout.split("\n")
    files = [f for f in files if f]
    errs = check(pr.get("body") or "", files, ".",
                 [l["name"] for l in pr.get("labels", [])], pr["user"]["login"])
    if errs:
        print("INSTRUCTION GATE FAILED (AGENTS.md law 15: Lock the method)")
        for e in errs:
            print(f"::error::{e}")
        sys.exit(1)
    print("Instruction gate passed.")


if __name__ == "__main__":
    main()
