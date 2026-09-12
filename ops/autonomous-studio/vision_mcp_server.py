from pathlib import Path
import hashlib, mimetypes, os
from mcp.server.fastmcp import FastMCP, Image
ROOT=Path(os.environ.get("STUDIO_ROOT","/workspace")).resolve()
EVIDENCE=ROOT/os.environ.get("EVIDENCE_DIR","artifacts/evidence")
mcp=FastMCP("studio-vision")
def digest(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for c in iter(lambda:f.read(1048576),b""): h.update(c)
 return h.hexdigest()
@mcp.tool()
def list_images(limit:int=100):
 out=[]
 for p in EVIDENCE.rglob("*"):
  if p.is_file() and p.suffix.lower() in {".png",".jpg",".jpeg",".webp"}:
   out.append({"path":str(p.relative_to(ROOT)),"sha256":digest(p),"bytes":p.stat().st_size})
   if len(out)>=limit: break
 return out
@mcp.tool()
def inspect_image(path:str):
 p=(ROOT/path).resolve()
 if not p.is_relative_to(ROOT) or not p.is_file(): raise ValueError("image missing/outside workspace")
 return {"path":str(p.relative_to(ROOT)),"sha256":digest(p),"mime":mimetypes.guess_type(p.name)[0],"bytes":p.stat().st_size}
@mcp.tool()
def view_image(path:str)->Image:
 p=(ROOT/path).resolve()
 if not p.is_relative_to(ROOT) or not p.is_file(): raise ValueError("image missing/outside workspace")
 mime=mimetypes.guess_type(p.name)[0] or "image/png"
 return Image(data=p.read_bytes(),format=mime.split("/")[-1])
if __name__=="__main__": mcp.run(transport="streamable-http")
