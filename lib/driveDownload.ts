import fs from 'fs';
import https from 'https';
import type { Hash } from 'crypto';

/**
 * Fetch a PUBLIC Drive file, following Drive's two non-obvious paths:
 *  - a 302/303 to the real host, and
 *  - the interstitial HTML page Drive serves for larger files, which carries a
 *    `confirm=` token and a cookie that must be echoed back on the retry.
 *
 * The hash is updated from the SAME chunks that are written to disk, so the
 * digest describes the bytes that actually landed rather than a second read of
 * the file that could differ.
 */
export function downloadDriveFile(
  fileId: string,
  dest: string,
  hash: Hash,
): Promise<number> {
  return new Promise((resolve, reject) => {
    let bytesRead = 0;
    const url = `https://drive.google.com/uc?export=download&id=${fileId}`;

    const sink = (res: NodeJS.ReadableStream) => {
      const fileStream = fs.createWriteStream(dest);
      res.on('data', (chunk: Buffer) => {
        hash.update(chunk);
        bytesRead += chunk.length;
      });
      res.pipe(fileStream);
      fileStream.on('finish', () => resolve(bytesRead));
      fileStream.on('error', reject);
      res.on('error', reject);
    };

    https
      .get(url, (res) => {
        if (res.statusCode === 302 || res.statusCode === 303) {
          const redirect = res.headers.location;
          if (!redirect) return reject(new Error('Drive redirect had no location header'));
          https.get(redirect, sink).on('error', reject);
        } else if (res.headers['set-cookie']) {
          let data = '';
          res.on('data', (chunk) => (data += chunk));
          res.on('end', () => {
            const match = data.match(/confirm=([0-9A-Za-z_]+)/);
            if (!match) return reject(new Error('Drive download confirm token not found'));
            const confirmUrl = `${url}&confirm=${match[1]}`;
            const cookies = (res.headers['set-cookie'] as string[]).join(';');
            https
              .get(confirmUrl, { headers: { Cookie: cookies } }, sink)
              .on('error', reject);
          });
        } else {
          sink(res);
        }
      })
      .on('error', reject);
  });
}
