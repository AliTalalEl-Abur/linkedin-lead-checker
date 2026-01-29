/**
 * PROMPT 10 — Popup UI Complete Pipeline
 *
 * End-to-end flow: LinkedIn Profile → Popup UI → Backend → Results Display
 *
 * This document explains the complete user flow and implementation details.
 */

// ============================================================================
// COMPLETE PIPELINE
// ============================================================================

/*
STEP 1: USER OPENS EXTENSION ON LINKEDIN PROFILE
  - User navigates to: https://www.linkedin.com/in/janesmith/
  - User clicks the "🔍 Lead Checker" extension icon
  - popup.html loads
  - popup.js checks chrome.storage.local for authToken
  
  RESULT:
    - If token exists → Show "Analyze Current Profile" button
    - If no token → Show "Login" screen

STEP 2: LOGIN
  - User enters email address
  - User clicks "Login" button (or presses Enter)
  - popup.js sends POST /auth/login with { email }
  - Backend creates/retrieves user, returns { access_token }
  - popup.js stores token in chrome.storage.local
  - popup.js transitions to "Analyze" section
  
  API CALL:
    POST BACKEND_URL/auth/login
    Body: { email: "user@example.com" }
    Response: { access_token: "eyJhbGc..." }

STEP 3: ANALYZE CURRENT PROFILE
  - User clicks "Analyze Current Profile" button
  - popup.js sends message to content.js (via chrome.tabs.sendMessage)
  - content.js (running on linkedin.com) extracts profile data
  - profile_extract object is returned to popup.js
  
  EXTRACTED DATA:
    {
      name: "Jane Smith",
      headline: "VP of Engineering at TechCorp",
      about: "Passionate about scaling engineering teams...",
      experience_titles: ["VP of Engineering", "Senior Engineer", ...],
      url: "https://www.linkedin.com/in/janesmith/",
      timestamp: "2026-01-19T12:34:56.789Z"
    }

STEP 4: SEND TO BACKEND
  - popup.js sends POST /analyze/linkedin with { profile_extract }
  - Authorization header includes Bearer token
  - Backend runs:
    - Check usage limits (free: 5/week, pro: 500/week)
    - Load user's ICP config or default
    - Run fit_scorer (JSON-only OpenAI client)
    - Run decision_writer (JSON-only OpenAI client)
    - Record usage event
    - Return results
  
  API CALL:
    POST BACKEND_URL/analyze/linkedin
    Headers: { Authorization: "Bearer <token>" }
    Body: { profile_extract: {...} }
    Response: {
      qualification: {
        overall_score: 85.0,
        dimension_scores: {...},
        positive_signals: [...],
        negative_signals: [...],
        data_quality: 90.0,
        confidence: 85.0
      },
      ui: {
        should_contact: true,
        priority: "high",
        score: 85.0,
        reasoning: "Strong match...",
        key_points: [...],
        suggested_approach: "Lead with...",
        red_flags: [...],
        next_steps: "Send message..."
      },
      plan: "free"
    }

STEP 5: DISPLAY RESULTS
  - popup.js receives response
  - Formats and displays results in readable format:
    - Decision (CONTACT / DON'T CONTACT)
    - Priority badge (HIGH / MEDIUM / LOW)
    - Score (0-100)
    - Reasoning (2-3 sentences)
    - Key Points (bulleted list)
    - Suggested Approach (personalized message)
    - Red Flags (if any)
    - Next Steps (actionable)
    - Metadata (plan, confidence, data quality)

STEP 6: LOGOUT (Optional)
  - User clicks "Logout"
  - popup.js clears chrome.storage.local authToken
  - popup.js transitions back to Login screen
*/

// ============================================================================
// STORAGE IMPLEMENTATION
// ============================================================================

/*
JWT TOKEN STORAGE:
  - Stored in: chrome.storage.local (not cookies)
  - Key: "authToken"
  - Scope: Extension-only (not accessible to webpage JavaScript)
  - Persistence: Survives browser restart
  - Clearing: User logout or manual data clearing

chrome.storage.local.set({ authToken: token });
chrome.storage.local.get(["authToken"], (result) => {
  const token = result.authToken; // null if not found
});
chrome.storage.local.remove(["authToken"], () => {
  // Token cleared
});
*/

// ============================================================================
// ERROR HANDLING
// ============================================================================

/*
LOGIN ERRORS:
  - Invalid email format → "Please enter a valid email address"
  - Network error → "Could not reach server at BACKEND_URL"
  - Server error → Display error from API response

EXTRACTION ERRORS:
  - Wrong page → "Not on a LinkedIn profile page. Visit linkedin.com/in/someone/"
  - Missing data → "Could not extract name/headline from profile"
  - Content script not loaded → "Could not access this page"

ANALYSIS ERRORS:
  - 402 Payment Required → "Free plan limit exceeded (5/week). Upgrade to Pro."
  - 401 Unauthorized → "Session expired. Please login again." + clear token
  - 429 Too Many Requests → "Rate limit exceeded. Contact support."
  - 500 Server Error → "Server error. Try again later."
  - Network error → "Could not reach server"

ALL ERRORS:
  - Displayed in red banner at top of popup
  - User can dismiss and retry
  - Error persists if critical (don't auto-dismiss)
*/

// ============================================================================
// USER EXPERIENCE
// ============================================================================

/*
LOADING STATES:
  - Login button shows "Logging in..." while waiting
  - Analyze button shows spinner + "Extracting profile..." then "Analyzing..."
  - Results display smooth transition (fade-in)

TRANSITIONS:
  - Login → Analyze: 500ms delay to show success message
  - Analyze → Results: Instant display once results received

STATUS MESSAGES:
  - Success: Green, auto-dismiss after 3 seconds (or disappear when action done)
  - Error: Red, persistent until user dismisses by clicking or trying again
  - Info: Blue, auto-dismiss

KEYBOARD SHORTCUTS:
  - Enter in email field: Submit login
  - Tab: Navigate between fields
*/

// ============================================================================
// MINIMALLIST APPROACH (No React, No Build Step)
// ============================================================================

/*
TECHNOLOGIES USED:
  ✅ Vanilla JavaScript (ES6)
  ✅ Plain HTML/CSS (no build tools needed)
  ✅ Chrome Storage API
  ✅ Chrome Messaging API
  ✅ Fetch API (no axios needed)

ADVANTAGES:
  - Fast load time (no JS bundles)
  - No dependency on React, Vue, etc.
  - Works offline (except API calls)
  - Easy to modify and debug
  - Small file sizes (< 50KB total)

FILE SIZES:
  - popup.html: ~7 KB
  - popup.js: ~10 KB
  - content.js: ~5 KB
  - background.js: < 1 KB
  - manifest.json: < 1 KB
  TOTAL: ~24 KB (uncompressed)
*/

// ============================================================================
// TESTING THE PIPELINE
// ============================================================================

/*
MANUAL TEST STEPS:

1. Start the backend API:
   C:/Users/LENOVO/Desktop/linkedin-lead-checker/.venv/Scripts/python.exe run.py

2. Load extension in Chrome:
   - Go to chrome://extensions/
   - Enable Developer mode
   - Click "Load unpacked"
   - Select linkedin-lead-checker/extension/

3. Open LinkedIn profile (e.g., linkedin.com/in/linkedin/ or any profile)

4. Click extension icon, see popup

5. Enter email and click Login
   - Should see "Login successful" message
   - Should transition to "Analyze" section

6. Click "Analyze Current Profile"
   - Should see "Extracting profile..." then "Analyzing..."
   - Profile data logged to console (if you inspect popup)

7. See results displayed:
   - Green banner: "Analysis complete!"
   - Results card showing decision, score, reasoning, etc.

8. Click "Logout"
   - Should return to login screen
   - Token cleared from storage

CHROME DEVTOOLS:
  - Right-click extension icon → "Inspect popup" to see console
  - Application → Storage → Local Storage → "chrome-extension://..." to see authToken
  - Network tab to see API calls
*/

// ============================================================================
// CONFIGURATION
// ============================================================================

/*
To change API endpoint (for production deployment):

In extension/popup.js:
  const API_CONFIG = {
    baseUrl: "https://api.example.com", // Change this
    loginEndpoint: "/auth/login",
    analyzeEndpoint: "/analyze/linkedin",
  };

In extension/src/background.js:
  const API_CONFIG = {
    baseUrl: "https://api.example.com", // Keep in sync
    analyzeEndpoint: "/analyze/linkedin",
  };
*/
