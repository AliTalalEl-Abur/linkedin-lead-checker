/**
 * Background Service Worker (MV3)
 * Handles minimal background tasks
 * Main API communication happens in popup.js
 */

// Open welcome page on first install
chrome.runtime.onInstalled.addListener((details) => {
  // Open welcome page only on first install (not on updates)
  if (details.reason === 'install') {
    chrome.tabs.create({
      url: chrome.runtime.getURL('welcome.html')
    });
  }
});

// Listen for messages from popup or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "log") {
    sendResponse({ success: true });
  }
});

