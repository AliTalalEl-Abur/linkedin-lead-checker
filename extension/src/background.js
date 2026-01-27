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

// Listen for messages from external websites (billing pages)
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
  console.log('External message received:', request, 'from:', sender.url);
  
  if (request.action === "ping") {
    // Respond to ping to confirm extension is installed
    sendResponse({ 
      installed: true, 
      version: chrome.runtime.getManifest().version 
    });
  } else if (request.action === "openPopup") {
    // Open the extension popup/dashboard
    chrome.action.openPopup()
      .then(() => {
        sendResponse({ success: true });
      })
      .catch((error) => {
        // If openPopup fails (not allowed from background), try opening a new tab
        chrome.tabs.create({
          url: chrome.runtime.getURL('popup.html')
        });
        sendResponse({ success: true, method: 'new_tab' });
      });
    return true; // Keep channel open for async response
  } else if (request.action === "openWelcome") {
    // Open welcome page
    chrome.tabs.create({
      url: chrome.runtime.getURL('welcome.html')
    });
    sendResponse({ success: true });
  }
  
  return true; // Keep the message channel open for async responses
});
