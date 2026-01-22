/**
 * Popup Script: Authentication Flow
 * - Login with email/password
 * - Store token securely in chrome.storage.local
 * - Persist login state on popup load
 */

const API_CONFIG = {
  baseUrl: "https://linkedin-lead-checker-api.onrender.com",
  loginEndpoint: "/auth/login",
};

// DOM Elements
const loginForm = document.getElementById("authForm");
const emailInput = document.getElementById("emailInput");
const passwordInput = document.getElementById("passwordInput");
const loginButton = document.getElementById("loginButton");
const statusMessage = document.getElementById("statusMessage");
const loginFormContainer = document.getElementById("loginForm");
const loggedInView = document.getElementById("loggedInView");
const userEmailDisplay = document.getElementById("userEmail");
const logoutButton = document.getElementById("logoutButton");

// Initialize on popup load
document.addEventListener("DOMContentLoaded", () => {
  checkLoginStatus();
  setupEventListeners();
});

/**
 * Check if user is already logged in
 */
function checkLoginStatus() {
  chrome.storage.local.get(["access_token", "email"], (result) => {
    if (result.access_token) {
      showLoggedInView(result.email);
    } else {
      showLoginForm();
    }
  });
}

/**
 * Show login form
 */
function showLoginForm() {
  loginFormContainer.style.display = "block";
  loggedInView.style.display = "none";
  clearForm();
}

/**
 * Show logged-in state
 */
function showLoggedInView(email) {
  loginFormContainer.style.display = "none";
  loggedInView.style.display = "block";
  userEmailDisplay.textContent = `Logged in as: ${email}`;
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
  loginForm.addEventListener("submit", handleLogin);
  logoutButton.addEventListener("click", handleLogout);
}

/**
 * Handle login form submission
 */
async function handleLogin(e) {
  e.preventDefault();

  const email = emailInput.value.trim();
  const password = passwordInput.value.trim();

  if (!email || !password) {
    showStatus("Please fill in all fields", "error");
    return;
  }

  setLoading(true);
  showStatus("Logging in...", "info");

  try {
    const response = await fetch(
      `${API_CONFIG.baseUrl}${API_CONFIG.loginEndpoint}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage =
        errorData.detail || "Login failed. Please try again.";
      showStatus(errorMessage, "error");
      setLoading(false);
      return;
    }

    const data = await response.json();

    if (!data.access_token) {
      showStatus("Invalid response from server", "error");
      setLoading(false);
      return;
    }

    // Store token and email securely
    chrome.storage.local.set(
      {
        access_token: data.access_token,
        email: email,
      },
      () => {
        showStatus("Login successful!", "success");
        setLoading(false);

        // Transition to logged-in view after short delay
        setTimeout(() => {
          showLoggedInView(email);
        }, 500);
      }
    );
  } catch (error) {
    console.error("Login error:", error);
    showStatus(
      error.message || "Network error. Please check your connection.",
      "error"
    );
    setLoading(false);
  }
}

/**
 * Handle logout
 */
function handleLogout() {
  chrome.storage.local.remove(["access_token", "email"], () => {
    showLoginForm();
    showStatus("Logged out successfully", "success");

    // Clear status after 2 seconds
    setTimeout(() => {
      clearStatus();
    }, 2000);
  });
}

/**
 * Show status message
 */
function showStatus(message, type) {
  statusMessage.textContent = message;
  statusMessage.className = `status visible ${type}`;
}

/**
 * Clear status message
 */
function clearStatus() {
  statusMessage.textContent = "";
  statusMessage.className = "status";
}

/**
 * Set loading state on button
 */
function setLoading(isLoading) {
  loginButton.disabled = isLoading;
  emailInput.disabled = isLoading;
  passwordInput.disabled = isLoading;

  if (isLoading) {
    loginButton.classList.add("loading");
    loginButton.textContent = "Logging in...";
  } else {
    loginButton.classList.remove("loading");
    loginButton.textContent = "Login";
  }
}

/**
 * Clear form inputs
 */
function clearForm() {
  emailInput.value = "";
  passwordInput.value = "";
  clearStatus();
}


// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener("DOMContentLoaded", async () => {
  const token = await getStoredToken();
  if (token) {
    showAnalyzeSection();
    showStatus("Logged in. Ready to analyze.", "info");
    // Load user stats
    await loadUserStats();
  } else {
    showAuthSection();
  }
  
  // Set up upgrade button handlers (Pro / Team)
  if (elements.upgradeButtons && elements.upgradeButtons.length) {
    elements.upgradeButtons.forEach((btn) => {
      btn.addEventListener("click", () => handleUpgrade(btn.dataset.plan || "pro", btn));
    });
  }
  
  // Set up dashboard button handler
  if (elements.dashboardBtn) {
    elements.dashboardBtn.addEventListener("click", () => {
      chrome.tabs.create({ url: "http://127.0.0.1:8001/../web/dashboard.html" });
    });
  }
});

// ============================================================================
// LOGIN
// ============================================================================

elements.loginBtn.addEventListener("click", async () => {
  const email = elements.emailInput.value.trim();
  
  if (!email) {
    showStatus("Please enter an email address", "error");
    elements.emailInput.focus();
    return;
  }

  if (!isValidEmail(email)) {
    showStatus("Please enter a valid email address", "error");
    return;
  }

  elements.loginBtn.disabled = true;
  const originalText = elements.loginBtn.textContent;
  elements.loginBtn.textContent = "Logging in...";

  try {
    const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.loginEndpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Login failed" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    const data = await response.json();
    if (!data.access_token) {
      throw new Error("No token received from server");
    }

    // Store token and transition to analyze view
    await storeToken(data.access_token);
    showStatus("✅ Login successful!", "success");
    elements.emailInput.value = "";
    
    setTimeout(async () => {
      showAnalyzeSection();
      await loadUserStats();
    }, 500);
  } catch (error) {
    console.error("Login error:", error);
    showStatus(`❌ Login failed: ${error.message}`, "error");
    elements.loginBtn.disabled = false;
    elements.loginBtn.textContent = originalText;
  }
});

// Allow Enter key to login
elements.emailInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    elements.loginBtn.click();
  }
});

// ============================================================================
// ANALYZE
// ============================================================================

elements.analyzeBtn.addEventListener("click", async () => {
  elements.analyzeBtn.disabled = true;
  elements.analyzeBtn.innerHTML = '<span class="spinner"></span> Extracting profile...';
  elements.resultSection.classList.remove("visible");
  showStatus("", ""); // Clear previous status

  try {
    // Step 1: Get active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    // Step 2: Extract profile from content script
    let response;
    try {
      response = await chrome.tabs.sendMessage(tab.id, { action: "extractProfile" });
    } catch (error) {
      throw new Error(
        "Could not access this page. Make sure you're on a LinkedIn profile (linkedin.com/in/someone/)"
      );
    }

    if (!response.success) {
      throw new Error(response.error || "Failed to extract profile");
    }

    const profileData = response.data;
    
    // Step 3: Validate minimum required fields
    if (!profileData.name || !profileData.headline) {
      throw new Error("Could not extract name or headline from this profile. Try refreshing the page.");
    }

    elements.analyzeBtn.innerHTML = '<span class="spinner"></span> Analyzing...';
    showStatus("Extracted profile. Analyzing with AI...", "info");

    // Step 4: Send to backend
    const token = await getStoredToken();
    if (!token) {
      throw new Error("No auth token. Please login again.");
    }

    const apiResponse = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.analyzeEndpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ profile_extract: profileData }),
    });

    if (!apiResponse.ok) {
      const errorData = await apiResponse.json().catch(() => ({ detail: "API error" }));
      
      if (apiResponse.status === 402) {
        // Payment required - show upgrade section
        showUpgradeSection(errorData.detail || "You've used your 3 free lead checks. Upgrade to keep analyzing.");
        throw new Error(errorData.detail || "Free plan limit reached. Upgrade to continue.");
      } else if (apiResponse.status === 401) {
        // Token expired
        await clearToken();
        showAuthSection();
        throw new Error("Session expired. Please login again.");
      } else {
        throw new Error(errorData.detail || `API error: ${apiResponse.status}`);
      }
    }

    const result = await apiResponse.json();
    
    // Step 5: Display results
    displayResult(result, profileData);
    showStatus("✅ Analysis complete!", "success");
    
    // Reload user stats to update usage count
    await loadUserStats();

  } catch (error) {
    console.error("Analyze error:", error);
    showStatus(`❌ ${error.message}`, "error");
  } finally {
    elements.analyzeBtn.disabled = false;
    elements.analyzeBtn.innerHTML = "Analyze Current Profile";
  }
});

// ============================================================================
// LOGOUT
// ============================================================================

elements.logoutBtn.addEventListener("click", async () => {
  await clearToken();
  showStatus("Logged out", "info");
  elements.emailInput.value = "";
  elements.emailInput.focus();
  showAuthSection();
});

// ============================================================================
// DISPLAY RESULTS
// ============================================================================

function displayResult(data, profileData) {
  const { qualification, ui, plan } = data;

  const scoreClass =
    ui.priority === "high"
      ? "score-high"
      : ui.priority === "medium"
      ? "score-medium"
      : "score-low";

  const priorityBadgeClass =
    ui.priority === "high"
      ? "priority-high"
      : ui.priority === "medium"
      ? "priority-medium"
      : "priority-low";

  // Traffic light logic
  const lights = {
    red: ui.priority === "low" ? "active-red" : "",
    yellow: ui.priority === "medium" ? "active-yellow" : "",
    green: ui.priority === "high" ? "active-green" : ""
  };

  let html = `
    <div class="result-header">
      <div class="traffic-light">
        <div class="light ${lights.green}"></div>
        <div class="light ${lights.yellow}"></div>
        <div class="light ${lights.red}"></div>
      </div>
      <div class="score-circle ${scoreClass}">${Math.round(ui.score)}</div>
      <span class="priority-badge ${priorityBadgeClass}">${ui.priority} Priority</span>
    </div>

    <div class="quick-section">
      <div class="section-title">
        <span class="section-icon">💡</span>
        Key Insights
      </div>
      <ul class="bullet-list">
        ${ui.key_points.slice(0, 5).map((p) => `<li>${p}</li>`).join("")}
      </ul>
    </div>

    ${
      ui.red_flags && ui.red_flags.length > 0
        ? `
    <div class="quick-section" style="border-left-color: #dc3545; background: #fff5f5;">
      <div class="section-title" style="color: #dc3545;">
        <span class="section-icon">⚠️</span>
        Red Flags
      </div>
      <ul class="bullet-list red-flags">
        ${ui.red_flags.slice(0, 3).map((f) => `<li>${f}</li>`).join("")}
      </ul>
    </div>
    `
        : ""
    }

    <div class="action-box">
      <div class="action-label">📋 Next Step</div>
      <p class="action-text">${ui.next_steps}</p>
    </div>

    <div class="action-box" style="border-color: #28a745; background: #f8fff9;">
      <div class="action-label" style="color: #28a745;">💬 DM Angle</div>
      <p class="action-text">${ui.suggested_approach}</p>
    </div>
  `;

  elements.resultCard.innerHTML = html;
  elements.resultSection.classList.add("visible");
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function showStatus(message, type) {
  if (!message) {
    elements.status.className = "status";
    return;
  }
  elements.status.textContent = message;
  elements.status.className = `status ${type}`;
}

function showAuthSection() {
  elements.authSection.classList.add("visible");
  elements.analyzeSection.classList.remove("visible");
  elements.resultSection.classList.remove("visible");
}

function showAnalyzeSection() {
  elements.authSection.classList.remove("visible");
  elements.analyzeSection.classList.add("visible");
  if (elements.upgradeSection) {
    elements.upgradeSection.classList.remove("visible");
  }
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// ============================================================================
// STORAGE (chrome.storage.local)
// ============================================================================

/**
 * Retrieve stored JWT token from chrome.storage.local
 */
function getStoredToken() {
  return new Promise((resolve) => {
    chrome.storage.local.get(["authToken"], (result) => {
      resolve(result.authToken || null);
    });
  });
}

/**
 * Store JWT token in chrome.storage.local
 */
function storeToken(token) {
  return new Promise((resolve) => {
    chrome.storage.local.set({ authToken: token }, () => {
      resolve();
    });
  });
}

/**
 * Clear stored JWT token
 */
function clearToken() {
  return new Promise((resolve) => {
    chrome.storage.local.remove(["authToken"], () => {
      resolve();
    });
  });
}

// ============================================================================
// USER STATS & USAGE
// ============================================================================

/**
 * Load user stats and display usage info
 */
async function loadUserStats() {
  const token = await getStoredToken();
  if (!token || !elements.usageInfo) {
    return;
  }
  
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.userEndpoint}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        await clearToken();
        showAuthSection();
      }
      return;
    }
    
    const userData = await response.json();
    const { plan, usage } = userData;
    
    // Display usage info
    const usagePercent = Math.min((usage.used / usage.limit) * 100, 100);
    let planBadge = '🆓 FREE';
    let subtitle = `${usage.used}/${usage.limit}`;
    let note = '';
    if (plan === 'pro') {
      planBadge = '⭐ PRO';
      subtitle = `${usage.used}/${usage.limit} this week`;
      note = 'Unlimited lead checks (fair use: 100/week)';
    } else if (plan === 'team') {
      planBadge = '👥 TEAM';
      subtitle = `${usage.used}/${usage.limit} this week`;
      note = 'Team plan: 300/week (fair use)';
    } else {
      subtitle = `${usage.used}/${usage.limit} lifetime`;
      note = '3 free lead checks. No credit card.';
    }
    
    elements.usageInfo.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span style="font-weight: 600;">${planBadge}</span>
        <span style="font-size: 12px; color: #666;">${subtitle}</span>
      </div>
      <div style="background: #e5e7eb; height: 6px; border-radius: 3px; overflow: hidden;">
        <div style="background: ${usagePercent > 80 ? '#ef4444' : '#667eea'}; height: 100%; width: ${usagePercent}%; transition: width 0.3s;"></div>
      </div>
      <div style="margin-top:6px; font-size:11px; color:#555;">${note}</div>
    `;
    
    // Show/hide upgrade section based on plan
    if (plan === 'free' && usage.remaining === 0 && elements.upgradeSection) {
      showUpgradeSection("You've used your 3 free lead checks. Upgrade to Pro ($19/mo) or Team ($39/mo).");
    }
  } catch (error) {
    console.error("Failed to load user stats:", error);
  }
}

/**
 * Show upgrade section with message
 */
function showUpgradeSection(message) {
  if (!elements.upgradeSection) return;
  
  elements.analyzeSection.classList.remove("visible");
  elements.upgradeSection.classList.add("visible");
  
  const messageEl = elements.upgradeSection.querySelector("span.upgrade-copy") || elements.upgradeSection.querySelector(".upgrade-message");
  if (messageEl) {
    messageEl.textContent = message;
  }
}

/**
 * Handle upgrade button click
 */
async function handleUpgrade(plan = "pro", btnRef = null) {
  const token = await getStoredToken();
  if (!token) {
    showStatus("Please login first", "error");
    return;
  }
  
  const targetBtn = btnRef || elements.upgradeButtons?.[0];
  if (targetBtn) {
    targetBtn.disabled = true;
    targetBtn.textContent = "Creating checkout...";
  }
  
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.checkoutEndpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        return_url: "http://127.0.0.1:8001/../web/billing-return.html?session_id={CHECKOUT_SESSION_ID}",
        plan,
      }),
    });
    
    if (!response.ok) {
      throw new Error("Failed to create checkout session");
    }
    
    const data = await response.json();
    
    // Open Stripe Checkout in new tab
    chrome.tabs.create({ url: data.url });
    
    showStatus("✅ Opening checkout page...", "success");
  } catch (error) {
    console.error("Upgrade error:", error);
    showStatus(`❌ Upgrade failed: ${error.message}`, "error");
  } finally {
    if (targetBtn) {
      targetBtn.disabled = false;
      targetBtn.textContent = targetBtn.dataset.plan === 'team' ? 'Team $39/mo — 300/wk for teams' : 'Pro $19/mo — Unlimited (fair use 100/wk)';
    }
  }
}
