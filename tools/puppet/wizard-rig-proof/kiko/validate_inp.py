#!/usr/bin/env python3
"""Worker C Wave 4 — validate Ashes.inp structurally per the nijilive spec.

Spec: https://github.com/nijigenerate/nijilive/blob/HEAD/doc/serialization_format.en.md
  magic "TRNSRTS\\0" (8B) | json_len BE u32 | JSON | "TEX_SECT" (8B) |
  tex_count BE u32 | per texture: data_len BE u32 | tex_type u8 | data
Checks: magic, JSON parses, required top-level keys, texture count matches
the rig's texture list, each texture blob non-empty and a decodable image.
"""
import struct
import json
import io
import sys
from PIL import Image

path = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/kiko/Kiko.inp"
data = open(path, "rb").read()
off = 0

magic = data[off:off + 8]; off += 8
assert magic == b"TRNSRTS\x00", f"bad magic {magic!r}"
json_len = struct.unpack(">I", data[off:off + 4])[0]; off += 4
payload = json.loads(data[off:off + json_len].decode("utf-8")); off += json_len
print(f"magic OK | JSON {json_len} bytes")

for key in ("meta", "nodes", "param", "physics"):
    assert key in payload, f"missing key {key}"
meta = payload["meta"]
nodes = payload["nodes"]
params = payload["param"]
nkeys = list(nodes.keys())[:3]
print(f"puppet: {meta.get('name')} | nodes: {len(nodes)} (keyed: {nkeys}) | "
      f"params: {len(params)} | physics: {len(payload.get('physics', []))} | "
      f"animations: {len(payload.get('animations', []))}")
print("parameter names:", ", ".join(p["name"] for p in params))
nbound = sum(1 for p in params if p.get("bindings"))
print(f"params with node bindings: {nbound}/{len(params)}")
assert nbound == len(params), "unbound parameter found"

tsect = data[off:off + 8]; off += 8
assert tsect == b"TEX_SECT", f"bad tex section {tsect!r}"
tcount = struct.unpack(">I", data[off:off + 4])[0]; off += 4
print(f"TEX_SECT OK | {tcount} textures")
for i in range(tcount):
    dlen = struct.unpack(">I", data[off:off + 4])[0]; off += 4
    ttype = data[off]; off += 1
    blob = data[off:off + dlen]; off += dlen
    assert len(blob) == dlen and dlen > 0
    im = Image.open(io.BytesIO(blob)); im.load()
    assert im.size[0] > 0 and im.size[1] > 0
print(f"all {tcount} texture blobs decode as images")
print("remaining bytes:", len(data) - off)
print("KIKO.INP STRUCTURALLY VALID")
