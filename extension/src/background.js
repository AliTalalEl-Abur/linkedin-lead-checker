/**
 * Background Service Worker (MV3)
 * Handles minimal background tasks
 * Main API communication happens in popup.js
 */

// Log when extension is installed or updated
chrome.runtime.onInstalled.addListener(() => {
  console.log("LinkedIn Lead Checker extension installed/updated");
});

// Listen for messages from popup or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "log") {
    console.log("[LinkedIn Lead Checker]", request.message);
    sendResponse({ success: true });
  }
});

