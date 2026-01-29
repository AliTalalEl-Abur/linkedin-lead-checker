const fs = require('fs');
const path = require('path');

const runtimeConfig = {
  API_URL: process.env.NEXT_PUBLIC_API_URL || '',
  SITE_URL: process.env.NEXT_PUBLIC_SITE_URL || '',
  CHECKOUT_RETURN_URL: process.env.NEXT_PUBLIC_CHECKOUT_RETURN_URL || '',
  CHROME_WEBSTORE_URL: process.env.NEXT_PUBLIC_CHROME_WEBSTORE_URL || ''
};

const content = `window.RUNTIME_CONFIG = ${JSON.stringify(runtimeConfig, null, 2)};\n`;

const targets = [
  path.join(__dirname, '..', 'public', 'runtime-env.js'),
  path.join(__dirname, '..', 'runtime-env.js')
];

for (const target of targets) {
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, content, 'utf8');
}

console.log('runtime-env.js generated');
