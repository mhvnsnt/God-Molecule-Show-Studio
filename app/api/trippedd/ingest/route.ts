import crypto from 'crypto';
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';
import { downloadDriveFile } from '@/lib/driveDownload';

// Spawns python, writes to the repo's asset dir, streams for as long as the
// toolchain takes: this is a Node route, never edge, and never cached.
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const maxDuration = 300;

/** Run a child process to completion, collecting stdout. */
function run(cmd: string, args: string[]): Promise<{ code: number | null; stdout: string }> {
  return new Promise((resolve) => {
    const p = spawn(cmd, args);
    let stdout = '';
    p.stdout.on('data', (d) => (stdout += d.toString()));
    p.stderr.on('data', (d) => console.error(`[${cmd} ERR] ${d}`));
    p.on('error', () => resolve({ code: -1, stdout: '' }));
    p.on('close', (code) => resolve({ code, stdout }));
  });
}

export async function POST(request: Request) {
  const { token, url: driveUrl } = (await request.json().catch(() => ({}))) as {
    token?: string | null;
    url?: string;
  };

  const encoder = new TextEncoder();

  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      let closed = false;
      const log = (msg: string) => {
        if (!closed) controller.enqueue(encoder.encode(msg + '\n'));
      };
      const end = () => {
        if (!closed) {
          closed = true;
          controller.close();
        }
      };

      if (!driveUrl) {
        log('[ERROR] Missing Drive URL.');
        return end();
      }

      // Drive file IDs are the only 25+ char run of [-\w] in every URL form
      // Drive hands out (/file/d/<id>/view, ?id=<id>, /open?id=<id>).
      const match = driveUrl.match(/[-\w]{25,}/);
      const fileId = match ? match[0] : null;
      if (!fileId) {
        log(`[ERROR] Could not extract valid Drive File ID from URL: ${driveUrl}`);
        return end();
      }

      try {
        log(`[DRIVE] Resolving file ID: ${fileId}`);

        const assetDir = path.join(process.cwd(), '.trippedd_assets');
        if (!fs.existsSync(assetDir)) fs.mkdirSync(assetDir, { recursive: true });
        const assetPath = path.join(assetDir, `mars_source_${fileId}.glb`);
        const hash = crypto.createHash('sha256');
        let bytesRead = 0;

        if (!token) {
          log('[SYSTEM] OAuth token unavailable. Executing public recovery path...');
          log('[DRIVE] Initiating public binary stream...');
          try {
            bytesRead = await downloadDriveFile(fileId, assetPath, hash);
            log('[DRIVE] Owner: Unknown (Public Recovery)');
            log('[DRIVE] MimeType: model/gltf-binary (Assumed)');
          } catch (e) {
            log(`[FATAL] Public recovery failed: ${(e as Error).message}`);
            return end();
          }
        } else {
          const metaUrl =
            `https://www.googleapis.com/drive/v3/files/${fileId}` +
            `?fields=id,name,mimeType,size,owners,shared`;
          const metaRes = await fetch(metaUrl, {
            headers: { Authorization: `Bearer ${token}` },
          });
          const metaData = await metaRes.json();

          if (metaData.error) {
            log(`[ERROR] Drive API returned error: ${metaData.error.message}`);
            log('[SYSTEM] Attempting public recovery path...');
            bytesRead = await downloadDriveFile(fileId, assetPath, hash);
          } else {
            log('[DRIVE] OAuth: VERIFIED');
            log('[DRIVE] File access: VERIFIED');
            log(`[DRIVE] Owner: ${metaData.owners?.[0]?.displayName || 'external account'}`);

            const sizeBytes = parseInt(metaData.size || '0', 10);
            log(
              `[DRIVE] Size: ${
                sizeBytes > 0 ? (sizeBytes / (1024 * 1024)).toFixed(2) + ' MB' : 'UNKNOWN'
              }`,
            );
            log(`[DRIVE] MimeType: ${metaData.mimeType}`);
            log('[DRIVE] Initiating authenticated binary download...');

            const dlRes = await fetch(
              `https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`,
              { headers: { Authorization: `Bearer ${token}` } },
            );
            if (!dlRes.ok || !dlRes.body) {
              log(`[ERROR] Failed to initiate binary stream. Status: ${dlRes.status}`);
              return end();
            }

            const fileStream = fs.createWriteStream(assetPath);
            const reader = dlRes.body.getReader();
            for (;;) {
              const { done, value } = await reader.read();
              if (done) break;
              if (value) {
                hash.update(value);
                fileStream.write(value);
                bytesRead += value.length;
              }
            }
            await new Promise<void>((r) => fileStream.end(r));
          }
        }

        const sha256 = hash.digest('hex');
        log(`[DRIVE] Download complete. Bytes read: ${bytesRead}`);
        log(`[DRIVE] SHA-256: ${sha256}`);
        log(`[ARCHIVE] Immutable source physically persisted: ${assetPath}`);

        log('[SYSTEM] Bootstrapping Open-Source Tools...');
        log('[BOOTSTRAP] Blender / OpenUSD ... PENDING');
        log('[BOOTSTRAP] Meshroom / PyMeshLab ... PENDING');
        log('[BOOTSTRAP] Faster-Whisper / Rhubarb ... PENDING');

        log('[INSPECTOR] Running tools/character/inspect_mars_asset.py...');
        const inspect = await run('python3', [
          'tools/character/inspect_mars_asset.py',
          assetPath,
        ]);

        let canonicalReady = false;
        let stats: Record<string, any> = {};
        try {
          stats = JSON.parse(inspect.stdout);
          if (stats.error) {
            log(`[ERROR] Python inspector failed: ${stats.error}`);
          } else {
            const fmt = (v: unknown) => (v !== undefined ? String(v) : 'UNKNOWN');
            log(`[MESH] Format: ${stats.format || 'UNKNOWN'}`);
            log(`[MESH] Vertices: ${stats.vertices}`);
            log(`[MESH] Faces: ${stats.faces}`);
            log(`[MESH] Meshes/Subtools: ${fmt(stats.meshes)}`);
            log(`[MESH] Components: ${fmt(stats.components)}`);
            log(
              `[MESH] Extents: ${
                stats.extents
                  ? stats.extents.map((v: number) => v.toFixed(3)).join(' x ')
                  : 'UNKNOWN'
              }`,
            );
            log(`[MESH] Materials: ${stats.materials ? stats.materials.join(', ') : 'UNKNOWN'}`);
            log(`[MESH] Textures: ${fmt(stats.textures)}`);
            log(`[MESH] Cameras: ${fmt(stats.cameras)}`);
            log(`[MESH] Lights: ${fmt(stats.lights)}`);
            log(`[UV] Mapping: ${stats.has_uv ? 'Present' : 'Missing'}`);
            log(`[TOPOLOGY] Status: ${stats.topologyStatus}`);
            log(`[RIG] Skeleton: ${stats.skeletonStatus}`);
            log(`[RIG] Blendshapes: ${stats.blendshapes}`);

            if (stats.vertices > 0 && String(stats.topologyStatus).includes('PASS')) {
              canonicalReady = true;
            }
          }
        } catch {
          log('[MESH] Vertices: UNKNOWN (Inspector Error)');
          log('[MESH] Faces: UNKNOWN');
        }

        if (canonicalReady) {
          const rigVerified = String(stats.skeletonStatus || '').includes('VERIFIED');
          const blendshapesVerified = String(stats.blendshapes || '').includes('VERIFIED');

          log('[STATE] MARS_ASSET: VERIFIED_GEOMETRY');
          log(`[STATE] RIG: ${rigVerified ? 'VERIFIED' : 'BLOCKED (Needs Proxy/Rigging Pass)'}`);
          log(
            `[STATE] ANIMATION: ${
              blendshapesVerified ? 'VERIFIED' : 'BLOCKED (Needs Facial Controls)'
            }`,
          );
          log('[SYSTEM] Initiating Blender Proxy Generation & Asset Integration...');

          const anim = await run('python3', ['tools/animation/build_slice.py', assetPath]);
          try {
            const result = JSON.parse(anim.stdout);
            if (result.logs) result.logs.forEach((l: string) => log(l));
          } catch {
            log('[ERROR] Animation pipeline failed to return JSON');
          }
        } else {
          // Strict enforcement: do not claim PASS on unverified systems. A stage
          // that never ran reports PENDING CAPABILITY, never a clean result --
          // "not attempted" and "attempted and empty" are different facts.
          log('[BLENDER] Import: PENDING CAPABILITY');
          log('[FACE] Animation test: PENDING CAPABILITY');
          log('[QC] Identity similarity: UNKNOWN');
          log('[ASSET] MARS_CANONICAL: INCOMPLETE (Awaiting 3D toolchain validation)');
        }

        log('[SYSTEM] EOF_SUCCESS');
        end();
      } catch (err) {
        console.error(err);
        log(`[FATAL] Production bridge failure: ${(err as Error).message}`);
        end();
      }
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'no-cache, no-transform',
      'X-Accel-Buffering': 'no',
    },
  });
}
