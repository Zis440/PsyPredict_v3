const crypto = require('crypto');
const child_process = require('child_process');
const fs = require('fs');

async function main() {
  const { privateKey } = crypto.generateKeyPairSync('rsa', {
    modulusLength: 2048,
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });

  const escapedKey = privateKey.replace(/\r/g, '').replace(/\n/g, '\\n');

  try {
     const run = `npx convex env set JWT_PRIVATE_KEY "${escapedKey}"`;
     fs.writeFileSync('temp.ps1', run);
     child_process.execSync('powershell.exe -ExecutionPolicy Bypass -File temp.ps1', {stdio: 'inherit'});
     console.log('Success via powershell file execute!');
  } catch (err) {
     console.error('Failed to set env', err.message);
  }
}

main().catch(console.error);
