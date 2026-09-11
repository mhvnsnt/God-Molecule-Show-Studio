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

  // Helper to download public drive files
  function downloadDriveFile(fileId, dest, log, hash) {
    return new Promise((resolve, reject) => {
      let bytesRead = 0;
      const url = `https://drive.google.com/uc?export=download&id=${fileId}`;
      
      const req = https.get(url, (res) => {
        if (res.statusCode === 302 || res.statusCode === 303) {
          const redirect = res.headers.location;
          https.get(redirect, (res2) => {
            const fileStream = fs.createWriteStream(dest);
            res2.on('data', chunk => {
                hash.update(chunk);
                bytesRead += chunk.length;
            });
            res2.pipe(fileStream);
            res2.on('end', () => resolve(bytesRead));
            res2.on('error', reject);
          }).on('error', reject);
        } else if (res.headers['set-cookie']) {
          let data = '';
          res.on('data', chunk => data += chunk);
          res.on('end', () => {
             const match = data.match(/confirm=([0-9A-Za-z_]+)/);
             if (match) {
                 const confirmUrl = url + '&confirm=' + match[1];
                 const cookies = res.headers['set-cookie'].join(';');
                 https.get(confirmUrl, { headers: { Cookie: cookies } }, (res3) => {
                     const fileStream = fs.createWriteStream(dest);
                     res3.on('data', chunk => {
                         hash.update(chunk);
                         bytesRead += chunk.length;
                     });
                     res3.pipe(fileStream);
                     res3.on('end', () => resolve(bytesRead));
                     res3.on('error', reject);
                 }).on('error', reject);
             } else {
                 reject(new Error("Drive download confirm token not found"));
             }
          });
        } else {
           const fileStream = fs.createWriteStream(dest);
           res.on('data', chunk => {
               hash.update(chunk);
               bytesRead += chunk.length;
           });
           res.pipe(fileStream);
           res.on('end', () => resolve(bytesRead));
           res.on('error', reject);
        }
      }).on('error', reject);
    });
  }

  app.post("/api/trippedd/ingest", async (req, res) => {
    const { token, url: driveUrl } = req.body;
    
    // Set headers for chunked streaming to frontend terminal
    res.setHeader('Content-Type', 'text/plain; charset=utf-8');
    res.setHeader('Transfer-Encoding', 'chunked');

    const log = (msg: string) => {
      res.write(msg + '\n');
    };

    if (!driveUrl) {
      log("[ERROR] Missing Drive URL.");
      return res.end();
    }

    // Attempt to extract file ID from common Drive URL formats
    const match = driveUrl.match(/[-\w]{25,}/);
    const fileId = match ? match[0] : null;

    if (!fileId) {
      log(`[ERROR] Could not extract valid Drive File ID from URL: ${driveUrl}`);
      return res.end();
    }

    try {
      log(`[DRIVE] Resolving file ID: ${fileId}`);
      
      const assetDir = path.join(process.cwd(), '.trippedd_assets');
      if (!fs.existsSync(assetDir)) {
        fs.mkdirSync(assetDir, { recursive: true });
      }
      const assetPath = path.join(assetDir, `mars_source_${fileId}.glb`);
      const hash = crypto.createHash('sha256');
      let bytesRead = 0;

      if (!token) {
         log(`[SYSTEM] OAuth token unavailable. Executing public recovery path...`);
         log(`[DRIVE] Initiating public binary stream...`);
         try {
             bytesRead = await downloadDriveFile(fileId, assetPath, log, hash) as number;
             log(`[DRIVE] Owner: Unknown (Public Recovery)`);
             log(`[DRIVE] MimeType: model/gltf-binary (Assumed)`);
         } catch (e: any) {
             log(`[FATAL] Public recovery failed: ${e.message}`);
             return res.end();
         }
      } else {
          // Use authenticated path
          const metaUrl = `https://www.googleapis.com/drive/v3/files/${fileId}?fields=id,name,mimeType,size,owners,shared`;
          
          const metaRes = await fetch(metaUrl, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          
          const metaData = await metaRes.json();
          
          if (metaData.error) {
            log(`[ERROR] Drive API returned error: ${metaData.error.message}`);
            log(`[SYSTEM] Attempting public recovery path...`);
            bytesRead = await downloadDriveFile(fileId, assetPath, log, hash) as number;
          } else {
              log(`[DRIVE] OAuth: VERIFIED`);
              log(`[DRIVE] File access: VERIFIED`);
              
              const ownerName = metaData.owners?.[0]?.displayName || "external account";
              log(`[DRIVE] Owner: ${ownerName}`);
              
              const sizeBytes = parseInt(metaData.size || "0", 10);
              const sizeStr = sizeBytes > 0 ? (sizeBytes / (1024 * 1024)).toFixed(2) + ' MB' : 'UNKNOWN';
              log(`[DRIVE] Size: ${sizeStr}`);
              log(`[DRIVE] MimeType: ${metaData.mimeType}`);

              log(`[DRIVE] Initiating authenticated binary download...`);
              
              const dlRes = await fetch(`https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`, {
                headers: { 'Authorization': `Bearer ${token}` }
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
                if (value) {
                  hash.update(value);
                  fileStream.write(value);
                  bytesRead += value.length;
                }
              }
              fileStream.end();
          }
      }

      const sha256 = hash.digest('hex');
      log(`[DRIVE] Download complete. Bytes read: ${bytesRead}`);
      log(`[DRIVE] SHA-256: ${sha256}`);
      log(`[ARCHIVE] Immutable source physically persisted: ${assetPath}`);

      log(`[SYSTEM] Bootstrapping Open-Source Tools...`);
      log(`[BOOTSTRAP] Blender / OpenUSD ... PENDING`);
      log(`[BOOTSTRAP] Meshroom / PyMeshLab ... PENDING`);
      log(`[BOOTSTRAP] Faster-Whisper / Rhubarb ... PENDING`);

      log(`[INSPECTOR] Running tools/character/inspect_mars_asset.py...`);
      
      const pyProcess = spawn('python3', ['tools/character/inspect_mars_asset.py', assetPath]);
      let pyOutput = '';
      
      pyProcess.stdout.on('data', (data) => {
          pyOutput += data.toString();
      });
      
      pyProcess.on('close', (code) => {
          let canonicalReady = false;
          try {
             const stats = JSON.parse(pyOutput);
             if (stats.error) {
                 log(`[ERROR] Python inspector failed: ${stats.error}`);
             } else {
                 log(`[MESH] Format: ${stats.format || 'UNKNOWN'}`);
                 log(`[MESH] Vertices: ${stats.vertices}`);
                 log(`[MESH] Faces: ${stats.faces}`);
                 log(`[MESH] Meshes/Subtools: ${stats.meshes !== undefined ? stats.meshes : 'UNKNOWN'}`);
                 log(`[MESH] Components: ${stats.components !== undefined ? stats.components : 'UNKNOWN'}`);
                 log(`[MESH] Extents: ${stats.extents ? stats.extents.map((v: number) => v.toFixed(3)).join(' x ') : 'UNKNOWN'}`);
                 log(`[MESH] Materials: ${stats.materials ? stats.materials.join(', ') : 'UNKNOWN'}`);
                 log(`[MESH] Textures: ${stats.textures !== undefined ? stats.textures : 'UNKNOWN'}`);
                 log(`[MESH] Cameras: ${stats.cameras !== undefined ? stats.cameras : 'UNKNOWN'}`);
                 log(`[MESH] Lights: ${stats.lights !== undefined ? stats.lights : 'UNKNOWN'}`);
                 log(`[UV] Mapping: ${stats.has_uv ? 'Present' : 'Missing'}`);
                 log(`[TOPOLOGY] Status: ${stats.topologyStatus}`);
                 log(`[RIG] Skeleton: ${stats.skeletonStatus}`);
                 log(`[RIG] Blendshapes: ${stats.blendshapes}`);
                 
                 if (stats.vertices > 0 && stats.topologyStatus.includes('PASS')) {
                     canonicalReady = true;
                     
                     // Attach stats for subsequent state checking
                     (res as any).assetStats = stats;
                 }
             }
          } catch(e) {
             log(`[MESH] Vertices: UNKNOWN (Inspector Error)`);
             log(`[MESH] Faces: UNKNOWN`);
          }

          if (canonicalReady) {
              const stats = (res as any).assetStats || {};
              const rigVerified = stats.skeletonStatus && stats.skeletonStatus.includes('VERIFIED');
              const blendshapesVerified = stats.blendshapes && stats.blendshapes.includes('VERIFIED');
              
              log(`[STATE] MARS_ASSET: VERIFIED_GEOMETRY`);
              log(`[STATE] RIG: ${rigVerified ? 'VERIFIED' : 'BLOCKED (Needs Proxy/Rigging Pass)'}`);
              log(`[STATE] ANIMATION: ${blendshapesVerified ? 'VERIFIED' : 'BLOCKED (Needs Facial Controls)'}`);
              
              log(`[SYSTEM] Initiating Blender Proxy Generation & Asset Integration...`);
              
              const animProcess = spawn('python3', ['tools/animation/build_slice.py', assetPath]);
              let animOutput = '';
              
              animProcess.stdout.on('data', (data) => { animOutput += data.toString(); });
              animProcess.stderr.on('data', (data) => { console.error(`[BLENDER ERR] ${data}`); });
              animProcess.on('close', () => {
                  try {
                      const result = JSON.parse(animOutput);
                      if (result.logs) {
                          result.logs.forEach((l: string) => log(l));
                      }
                  } catch (e) {
                      log(`[ERROR] Animation pipeline failed to return JSON`);
                  }
                  log(`[SYSTEM] EOF_SUCCESS`);
                  res.end();
              });
          } else {
              // Strict enforcement: Do not claim PASS on unverified systems.
              log(`[BLENDER] Import: PENDING CAPABILITY`);
              log(`[FACE] Animation test: PENDING CAPABILITY`);
              log(`[QC] Identity similarity: UNKNOWN`);
              log(`[ASSET] MARS_CANONICAL: INCOMPLETE (Awaiting 3D toolchain validation)`);
    
              log(`[SYSTEM] EOF_SUCCESS`);
              res.end();
          }
      });
      
    } catch (err: any) {
      console.error(err);
      log(`[FATAL] Production bridge failure: ${err.message}`);
      res.end();
    }
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`TRIPPEDD Bridge Server running on port ${PORT}`);
  });
}

startServer();
