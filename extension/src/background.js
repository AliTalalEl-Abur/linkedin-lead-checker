/**
 * Background Service Worker: Handles optional API calls and logging
 * Note: Most API communication is now handled directly from popup.js for simplicity
 */

const API_CONFIG = {
  baseUrl: "http://127.0.0.1:8000",
  analyzeEndpoint: "/analyze/linkedin",
};

// Optional: Log when extension is installed
chrome.runtime.onInstalled.addListener(() => {
  console.log("LinkedIn Lead Checker extension installed");
});

// Optional: Handle any future messaging (kept for extensibility)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "logEvent") {
    console.log("[LinkedIn Lead Checker]", request.message);
    sendResponse({ ok: true });
  }
});
