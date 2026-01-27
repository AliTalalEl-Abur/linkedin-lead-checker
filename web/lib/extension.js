/**
 * Hook for detecting and communicating with the Chrome extension
 */
import { useState, useEffect } from 'react';

// Extension ID will be constant after publishing to Chrome Web Store
// For development, this needs to be updated to match the unpacked extension ID
const EXTENSION_IDS = [
  'YOUR_EXTENSION_ID_HERE', // Production extension ID (from Chrome Web Store)
  // Add development extension IDs here if needed
];

/**
 * Detect if the Chrome extension is installed
 * @returns {Object} { isInstalled, isChecking, extensionId, sendMessage }
 */
export function useChromeExtension() {
  const [isInstalled, setIsInstalled] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [extensionId, setExtensionId] = useState(null);

  useEffect(() => {
    checkExtension();
  }, []);

  const checkExtension = async () => {
    if (typeof chrome === 'undefined' || !chrome.runtime) {
      // Not in Chrome or extension API not available
      setIsChecking(false);
      setIsInstalled(false);
      return;
    }

    // Try to ping each possible extension ID
    for (const id of EXTENSION_IDS) {
      try {
        await new Promise((resolve, reject) => {
          chrome.runtime.sendMessage(
            id,
            { action: 'ping' },
            (response) => {
              if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
              } else if (response && response.installed) {
                setIsInstalled(true);
                setExtensionId(id);
                resolve(response);
              } else {
                reject(new Error('Invalid response'));
              }
            }
          );
        });
        // If we get here, extension was found
        setIsChecking(false);
        return;
      } catch (error) {
        // Extension not found with this ID, continue to next
        continue;
      }
    }

    // No extension found
    setIsChecking(false);
    setIsInstalled(false);
  };

  /**
   * Send a message to the extension
   * @param {Object} message - Message to send
   * @returns {Promise<Object>} Response from extension
   */
  const sendMessage = async (message) => {
    if (!isInstalled || !extensionId) {
      throw new Error('Extension not installed');
    }

    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(
        extensionId,
        message,
        (response) => {
          if (chrome.runtime.lastError) {
            reject(chrome.runtime.lastError);
          } else {
            resolve(response);
          }
        }
      );
    });
  };

  /**
   * Open the extension popup/dashboard
   */
  const openExtension = async () => {
    try {
      const response = await sendMessage({ action: 'openPopup' });
      return response;
    } catch (error) {
      console.error('Failed to open extension:', error);
      throw error;
    }
  };

  return {
    isInstalled,
    isChecking,
    extensionId,
    sendMessage,
    openExtension,
    recheck: checkExtension,
  };
}

/**
 * Get the Chrome Web Store URL for the extension
 */
export function getChromeWebStoreUrl() {
  // Replace with actual extension ID after publishing
  return `https://chrome.google.com/webstore/detail/YOUR_EXTENSION_ID_HERE`;
}

/**
 * Check if user is on Chrome browser
 */
export function isChromeBrowser() {
  if (typeof window === 'undefined') return false;
  
  const isChrome = /Chrome/.test(navigator.userAgent) && /Google Inc/.test(navigator.vendor);
  const isEdge = /Edg/.test(navigator.userAgent);
  
  return isChrome || isEdge;
}
