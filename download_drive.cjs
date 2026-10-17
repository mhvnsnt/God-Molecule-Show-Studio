const https = require('https');
const fs = require('fs');

function downloadDrive(fileId, dest) {
    const url = `https://drive.google.com/uc?export=download&id=${fileId}`;
    return new Promise((resolve, reject) => {
        https.get(url, (res) => {
            if (res.statusCode === 302 || res.statusCode === 303) {
                // Handle redirect
                const redirect = res.headers.location;
                https.get(redirect, (res2) => {
                    const file = fs.createWriteStream(dest);
                    res2.pipe(file);
                    file.on('finish', () => { file.close(); resolve(); });
                }).on('error', reject);
            } else if (res.headers['set-cookie']) {
                 // Try to get download confirm token
                 let data = '';
                 res.on('data', chunk => data += chunk);
                 res.on('end', () => {
                     const match = data.match(/confirm=([0-9A-Za-z_]+)/);
                     if (match) {
                         const confirmUrl = url + '&confirm=' + match[1];
                         const cookies = res.headers['set-cookie'].join(';');
                         https.get(confirmUrl, { headers: { Cookie: cookies } }, (res3) => {
                             const file = fs.createWriteStream(dest);
                             res3.pipe(file);
                             file.on('finish', () => { file.close(); resolve(); });
                         }).on('error', reject);
                     } else {
                         // Maybe it's directly streaming?
                         reject(new Error("No confirm token found"));
                     }
                 });
            } else {
                const file = fs.createWriteStream(dest);
                res.pipe(file);
                file.on('finish', () => { file.close(); resolve(); });
            }
        }).on('error', reject);
    });
}
downloadDrive('1RKxHGkgoKe0hZf7a2kObqzKpgqKfkrhl', 'mars.obj').then(() => console.log('Downloaded')).catch(console.error);
