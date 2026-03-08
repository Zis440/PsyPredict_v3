const crypto = require('crypto');
const { execSync } = require('child_process');

async function main() {
  const k = await crypto.subtle.generateKey({name:'RSASSA-PKCS1-v1_5',modulusLength:2048,publicExponent:new Uint8Array([1,0,1]),hash:'SHA-256'},true,['sign','verify']);
  const jwk = await crypto.subtle.exportKey('jwk',k.privateKey);
  const keyStr = JSON.stringify(jwk);
  console.log('Generated JWK.');
  
  // Create a temporary file to avoid command line length limits/escaping quoting issues
  const fs = require('fs');
  fs.writeFileSync('temp_key.json', keyStr);
  
  console.log('Setting key in Convex...');
  execSync('npx convex env set JWT_PRIVATE_KEY "' + keyStr.replace(/"/g, '\\"') + '"', { stdio: 'inherit' });
  
  fs.unlinkSync('temp_key.json');
}

main().catch(console.error);
