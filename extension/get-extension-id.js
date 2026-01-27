/**
 * Helper script to get Chrome Extension ID
 * Run this in the browser console after loading the extension
 */

// Method 1: If you're on chrome://extensions/ page
console.log('=== Chrome Extension ID Helper ===\n');

// Method 2: Check from extension context
if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.id) {
  console.log('✅ Extension ID:', chrome.runtime.id);
  console.log('\nCopy this ID and update it in:');
  console.log('web/lib/extension.js → EXTENSION_IDS array');
} else {
  console.log('ℹ️  To get your Extension ID:');
  console.log('1. Open chrome://extensions/');
  console.log('2. Enable "Developer mode" (top right)');
  console.log('3. Look for "LinkedIn Lead Checker"');
  console.log('4. Copy the ID shown below the extension name');
  console.log('5. Update EXTENSION_IDS in web/lib/extension.js');
}

console.log('\n=================================');
