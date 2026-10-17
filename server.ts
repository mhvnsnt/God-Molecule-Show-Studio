import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import fs from "fs";
import crypto from "crypto";
import https from "https";
import { spawn } from "child_process";

async function startServer() {
  const app = express();
  const PORT = 3000;
  app.use(express.json());

  app.get("/api/health", (req, res) => {
    res.json({ status: "TRIPPEDD RUNTIME ONLINE" });
  });

  function downloadDriveFile(fileId: string, dest: string, hash: crypto.Hash) {
    return new Promise<number>((resolve, reject) => {
      const url = `https://drive.google.com/uc?export=download&id=${fileId}`;
      const req = https.get(url, (res) => {
        const finish = (response: any) => {
          const fileStream = fs.createWriteStream(dest);
          let bytesRead = 0;
          response.on("data", (chunk: Buffer) => { hash.update(chunk); bytesRead += chunk.length; });
          response.pipe(fileStream);
          response.on("end", () => resolve(bytesRead));
          response.on("error", reject);
        };
        if (res.statusCode === 302 || res.statusCode === 303) {
          const redirect = res.headers.location;
          if (!redirect) return reject(new Error("Drive redirect missing"));
          https.get(redirect, finish).on("error", reject);
        } else if (res.headers["set-cookie"]) {
          let data = "";
          res.on("data", chunk => data += chunk);
          res.on("end", () => {
            const match = data.match(/confirm=([0-9A-Za-z_]+)/);
            if (!match) return reject(new Error("Drive download confirm token not found"));
            const cookies = res.headers["set-cookie"]!.join("; ");
            https.get(url + "&confirm=" + match[1], { headers: { Cookie: cookies } }, finish).on("error", reject);
          });
        } else {
          finish(res);
        }
      }).on("error", reject);
    });
  }

  app.post("/api/trippedd/ingest", async (req, res) => {
    const { token, url: driveUrl, rhubarbJsonPath } = req.body as {
      token?: string;
      url?: string;
      rhubarbJsonPath?: string;
    };

    res.setHeader("Content-Type", "text/plain; charset=utf-8");
    res.setHeader("Transfer-Encoding", "chunked");
    const log = (msg: string) => res.write(msg + "\n");

    if (!driveUrl) {
      log("[ERROR] Missing Drive URL.");
      return res.end();
    }

    const match = driveUrl.match(/[-\w]{25,}/);
    const fileId = match ? match[0] : null;
    if (!fileId) {
      log("[ERROR] Could not extract valid Drive File ID.");
      return res.end();
    }

    try {
      const assetDir = path.join(process.cwd(), ".trippedd_assets");
      fs.mkdirSync(assetDir, { recursive: true });
      const assetPath = path.join(assetDir, `mars_source_${fileId}.glb`);
      const hash = crypto.createHash("sha256");
      let bytesRead = 0;

      if (!token) {
        log("[SYSTEM] OAuth token unavailable. Executing public recovery path...");
        bytesRead = await downloadDriveFile(fileId, assetPath, hash);
      } else {
        const metaRes = await fetch(`https://www.googleapis.com/drive/v3/files/${fileId}?fields=id,name,mimeType,size,owners,shared`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const metaData: any = await metaRes.json();
        if (metaData.error) {
          log("[ERROR] Drive API returned an error; attempting public recovery.");
          bytesRead = await downloadDriveFile(fileId, assetPath, hash);
        } else {
          log("[DRIVE] OAuth: VERIFIED");
          log(`[DRIVE] MimeType: ${metaData.mimeType || "UNKNOWN"}`);
          const dlRes = await fetch(`https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          if (!dlRes.ok || !dlRes.body) {
            log(`[ERROR] Failed to initiate binary stream. Status: ${dlRes.status}`);
            return res.end();
          }
          const fileStream = fs.createWriteStream(assetPath);
          const reader = dlRes.body.getReader();
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            if (value) { hash.update(value); fileStream.write(value); bytesRead += value.length; }
          }
          fileStream.end();
        }
      }

      log(`[DRIVE] Download complete. Bytes read: ${bytesRead}`);
      log(`[DRIVE] SHA-256: ${hash.digest("hex")}`);
      log("[ARCHIVE] Immutable source physically persisted.");

      log("[INSPECTOR] Running character inspection...");
      const pyProcess = spawn("python3", ["tools/character/inspect_mars_asset.py", assetPath]);
      let pyOutput = "";
      pyProcess.stdout.on("data", data => { pyOutput += data.toString(); });

      pyProcess.on("close", code => {
        let stats: any;
        try { stats = JSON.parse(pyOutput); }
        catch {
          log(`[MESH] Inspector returned invalid JSON (exit ${code ?? "UNKNOWN"}).`);
          log("[QC] Identity similarity: UNKNOWN");
          return res.end();
        }

        log(`[MESH] Vertices: ${stats.vertices ?? "UNKNOWN"}`);
        log(`[MESH] Faces: ${stats.faces ?? "UNKNOWN"}`);
        log(`[TOPOLOGY] Status: ${stats.topologyStatus ?? "UNKNOWN"}`);
        log(`[RIG] Skeleton: ${stats.skeletonStatus ?? "UNKNOWN"}`);
        log(`[RIG] Blendshapes: ${stats.blendshapes ?? "UNKNOWN"}`);

        if (!(stats.vertices > 0 && String(stats.topologyStatus).includes("PASS"))) {
          log("[STATE] MARS_ASSET: BLOCKED (geometry validation incomplete)");
          return res.end();
        }

        if (!rhubarbJsonPath || !fs.existsSync(rhubarbJsonPath)) {
          log("[FACE] Animation: BLOCKED (REAL_AUDIO_REQUIRED; supply Rhubarb JSON)");
          log("[RENDER] Not started — no invented transcript/cadence allowed.");
          return res.end();
        }

        log("[STATE] MARS_ASSET: VERIFIED_GEOMETRY");
        log("[SYSTEM] Starting real-audio Blender render...");
        const animProcess = spawn("python3", [
          "tools/animation/build_slice.py",
          assetPath,
          "--rhubarb-json",
          rhubarbJsonPath
        ]);
        let animOutput = "";
        animProcess.stdout.on("data", data => { animOutput += data.toString(); });
        animProcess.stderr.on("data", data => log(`[BLENDER] ${data.toString().trim()}`));
        animProcess.on("close", exitCode => {
          try {
            const result = JSON.parse(animOutput);
            for (const line of result.logs || []) log(line);
            if (result.visualEvidence) log(`[EVIDENCE] Human review packet: ${result.visualEvidence}`);
            log(`[STATE] ANIMATION: ${exitCode === 0 ? "REAL_RENDER" : "BLOCKED"}`);
          } catch {
            log("[STATE] ANIMATION: BLOCKED (pipeline returned no valid JSON)");
          }
          res.end();
        });
      });
    } catch (err: any) {
      log(`[FATAL] Production bridge failure: ${err.message}`);
      res.end();
    }
  });

  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({ server: { middlewareMode: true }, appType: "spa" });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (_req, res) => res.sendFile(path.join(distPath, "index.html")));
  }

  app.listen(PORT, "0.0.0.0", () => console.log(`TRIPPEDD Bridge Server running on port ${PORT}`));
}

startServer();
