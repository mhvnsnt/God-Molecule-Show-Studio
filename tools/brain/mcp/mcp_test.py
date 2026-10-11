#!/usr/bin/env python3
"""Smoke-test an MCP server over stdio: initialize -> tools/list -> print tool names.
Usage: python3 mcp_test.py <command...> [--timeout 15] [--env K=V ...]
Exits 0 if tools/list succeeded, 1 otherwise.
"""
import json, os, subprocess, sys, select

def read_msg(proc, timeout):
    ready, _, _ = select.select([proc.stdout], [], [], timeout)
    if not ready:
        raise TimeoutError("no response from server")
    line = proc.stdout.readline().decode().strip()
    return json.loads(line)

def send(proc, obj):
    proc.stdin.write((json.dumps(obj) + "\n").encode())
    proc.stdin.flush()

def main():
    args = sys.argv[1:]
    timeout = 15
    env_pairs = {}
    cmd = []
    i = 0
    while i < len(args):
        if args[i] == "--timeout":
            timeout = int(args[i + 1]); i += 2
        elif args[i] == "--env":
            k, v = args[i + 1].split("=", 1); env_pairs[k] = v; i += 2
        else:
            cmd.append(args[i]); i += 1
    env = dict(os.environ); env.update(env_pairs)
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env)
    try:
        send(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                    "params": {"protocolVersion": "2024-11-05",
                               "capabilities": {}, "clientInfo": {"name": "mcp-test", "version": "0.1"}}})
        resp = read_msg(proc, timeout)
        send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        # skip notifications, find id==2
        deadline = 3
        for _ in range(deadline):
            msg = read_msg(proc, timeout)
            if msg.get("id") == 2:
                resp = msg; break
        if resp.get("id") != 2:
            raise RuntimeError(f"unexpected response: {resp}")
        if "error" in resp:
            raise RuntimeError(f"tools/list error: {resp['error']}")
        tools = resp["result"]["tools"]
        names = [t["name"] for t in tools]
        print(f"OK: {len(tools)} tools")
        for n in names:
            print(f"  - {n}")
        return 0
    except Exception as e:
        print(f"FAIL: {e}")
        err = proc.stderr.read1().decode()[-2000:] if proc.stderr else ""
        if err: print("--- stderr tail ---\n" + err)
        return 1
    finally:
        proc.kill()

sys.exit(main())
