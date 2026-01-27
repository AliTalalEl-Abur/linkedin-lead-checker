/**
 * LinkedIn Lead Checker - Popup Script
 * Authentication and profile analysis functionality
 */

const API_CONFIG = {
  baseUrl: "https://linkedin-lead-checker-api.onrender.com",
  loginEndpoint: "/auth/login",
  billingStatusEndpoint: "/billing/status",
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
const analyzeButton = document.getElementById("analyzeButton");
const viewPricingButton = document.getElementById("viewPricingButton");
const resultsContainer = document.getElementById("resultsContainer");
const backButton = document.getElementById("backButton");
const unlockButton = document.getElementById("unlockButton");
const starRating = document.getElementById("starRating");
const insightsList = document.getElementById("insightsList");
const limitModal = document.getElementById("limitModal");
const upgradePlanButton = document.getElementById("upgradePlanButton");
const viewUsageButton = document.getElementById("viewUsageButton");
const closeModalButton = document.getElementById("closeModalButton");
const showFeedbackButton = document.getElementById("showFeedbackButton");
const feedbackSection = document.getElementById("feedbackSection");
const feedbackTextarea = document.getElementById("feedbackTextarea");
const submitFeedbackButton = document.getElementById("submitFeedbackButton");
const cancelFeedbackButton = document.getElementById("cancelFeedbackButton");
const feedbackStatus = document.getElementById("feedbackStatus");

// Initialize on popup load
document.addEventListener("DOMContentLoaded", () => {
  checkLoginStatus();
  setupEventListeners();
});

/**
 * Check if user is already logged in and update billing status
 */
async function checkLoginStatus() {
  chrome.storage.local.get(["access_token", "email"], async (result) => {
    if (result.access_token) {
      showLoggedInView(result.email);
      // Fetch and update billing status
      await updateBillingStatus(result.access_token);
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

// ============================================================================
// BILLING STATUS & PLAN MANAGEMENT
// ============================================================================

/**
 * Fetch billing status from backend (returns data without UI update)
 */
async function fetchBillingStatus(token) {
  try {
    const response = await fetch(
      `${API_CONFIG.baseUrl}${API_CONFIG.billingStatusEndpoint}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        }
      }
    );

    if (!response.ok) {
      console.error("Failed to fetch billing status:", response.status);
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching billing status:", error);
    return null;
  }
}

/**
 * Fetch and update billing status from backend
 * This ensures the extension UI reflects the latest subscription state
 * without requiring logout/login after payment
 */
async function updateBillingStatus(token) {
  try {
    const response = await fetch(
      `${API_CONFIG.baseUrl}${API_CONFIG.billingStatusEndpoint}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        }
      }
    );

    if (!response.ok) {
      console.error("Failed to fetch billing status:", response.status);
      // Don't show error to user - just use cached data
      return;
    }

    const billingData = await response.json();
    
    // Store billing data locally
    await chrome.storage.local.set({
      billing_status: billingData,
      billing_last_updated: Date.now()
    });

    // Check if plan changed
    chrome.storage.local.get(['cached_plan'], (result) => {
      const oldPlan = result.cached_plan || 'free';
      const newPlan = billingData.plan || 'free';
      
      if (oldPlan !== newPlan) {
        // Plan changed! Update UI
        handlePlanChange(oldPlan, newPlan, billingData);
      }
      
      // Always update cached plan
      chrome.storage.local.set({ cached_plan: newPlan });
    });

    // Update UI with current status
    updateUIWithBillingStatus(billingData);

  } catch (error) {
    console.error("Error fetching billing status:", error);
    // Fail silently - use cached data
  }
}

/**
 * Handle plan change event
 * Shows a notification to the user about their upgraded plan
 */
function handlePlanChange(oldPlan, newPlan, billingData) {
  // Show success message for upgrade
  if (newPlan !== 'free' && oldPlan === 'free') {
    const planNames = {
      'starter': 'Starter',
      'pro': 'Pro',
      'team': 'Team'
    };
    
    const planName = planNames[newPlan] || newPlan;
    showStatus(`🎉 Welcome to ${planName}! You now have ${billingData.usage_limit} analyses/month.`, "success");
    
    // Clear message after 5 seconds
    setTimeout(() => {
      clearStatus();
    }, 5000);
  }
}

/**
 * Update UI elements based on billing status
 * - Shows plan badge
 * - Updates usage information
 * - Shows/hides upgrade prompts
 */
function updateUIWithBillingStatus(billingData) {
  const plan = billingData.plan || 'free';
  const canAnalyze = billingData.can_analyze;
  const usageCurrent = billingData.usage_current || 0;
  const usageLimit = billingData.usage_limit || 0;
  
  // Update plan badge if it exists
  updatePlanBadge(plan);
  
  // Update usage display if it exists
  updateUsageDisplay(usageCurrent, usageLimit, canAnalyze);
  
  // Show/hide upgrade prompts based on plan
  updateUpgradePrompts(plan, canAnalyze);
}

/**
 * Update plan badge in UI
 */
function updatePlanBadge(plan) {
  let planBadge = document.getElementById('planBadge');
  
  // Create badge if it doesn't exist
  if (!planBadge) {
    planBadge = document.createElement('div');
    planBadge.id = 'planBadge';
    planBadge.className = 'plan-badge';
    
    const loggedInContent = document.querySelector('.logged-in-content');
    if (loggedInContent) {
      loggedInContent.insertBefore(planBadge, loggedInContent.firstChild);
    }
  }
  
  // Set badge content and style based on plan
  const planConfig = {
    'free': { label: 'Free Plan', class: 'plan-free' },
    'starter': { label: '⭐ Starter Plan', class: 'plan-starter' },
    'pro': { label: '🚀 Pro Plan', class: 'plan-pro' },
    'team': { label: '👥 Team Plan', class: 'plan-team' }
  };
  
  const config = planConfig[plan] || planConfig['free'];
  planBadge.textContent = config.label;
  planBadge.className = `plan-badge ${config.class}`;
}

/**
 * Update usage display in UI
 */
function updateUsageDisplay(current, limit, canAnalyze) {
  let usageDisplay = document.getElementById('usageDisplay');
  
  // Create usage display if it doesn't exist
  if (!usageDisplay) {
    usageDisplay = document.createElement('div');
    usageDisplay.id = 'usageDisplay';
    usageDisplay.className = 'usage-display';
    
    const loggedInContent = document.querySelector('.logged-in-content');
    if (loggedInContent) {
      loggedInContent.appendChild(usageDisplay);
    }
  }
  
  // Calculate percentage
  const percentage = limit > 0 ? Math.round((current / limit) * 100) : 0;
  
  // Set warning class if near limit
  const warningClass = percentage >= 80 ? 'usage-warning' : '';
  
  usageDisplay.className = `usage-display ${warningClass}`;
  usageDisplay.innerHTML = `
    <div class="usage-text">
      <span class="usage-label">Monthly Usage:</span>
      <span class="usage-count">${current} / ${limit}</span>
    </div>
    <div class="usage-bar">
      <div class="usage-bar-fill" style="width: ${percentage}%"></div>
    </div>
  `;
  
  // Update analyze button state
  if (analyzeButton) {
    analyzeButton.disabled = !canAnalyze;
    analyzeButton.title = canAnalyze ? 'Analyze current LinkedIn profile' : 'Monthly limit reached';
  }
}

/**
 * Update upgrade prompts visibility
 */
function updateUpgradePrompts(plan, canAnalyze) {
  // Hide "View Pricing" button for paid plans
  if (viewPricingButton) {
    if (plan !== 'free') {
      viewPricingButton.style.display = 'none';
    } else {
      viewPricingButton.style.display = 'block';
    }
  }
  
  // Show limit modal if can't analyze
  if (!canAnalyze && plan === 'free') {
    // Don't auto-show modal, just disable button
    // Modal will show when user tries to analyze
  }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
  loginForm.addEventListener("submit", handleLogin);
  logoutButton.addEventListener("click", handleLogout);
  analyzeButton.addEventListener("click", handleAnalyze);
  viewPricingButton.addEventListener("click", handleViewPricing);
  backButton.addEventListener("click", hideResults);
  unlockButton.addEventListener("click", handleViewPricing);
  upgradePlanButton.addEventListener("click", handleUpgrade);
  viewUsageButton.addEventListener("click", handleViewUsage);
  closeModalButton.addEventListener("click", closeLimitModal);
  showFeedbackButton.addEventListener("click", showFeedbackSection);
  submitFeedbackButton.addEventListener("click", handleSubmitFeedback);
  cancelFeedbackButton.addEventListener("click", hideFeedbackSection);
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
      
      // Check for soft launch limit reached
      if (response.status === 429 && errorData.detail?.limit_reached) {
        showStatus(errorData.detail.message || "Registration limit reached. Please try again tomorrow.", "error");
        setLoading(false);
        return;
      }
      
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
      async () => {
        showStatus("Login successful!", "success");
        setLoading(false);

        // Transition to logged-in view after short delay
        setTimeout(() => {
          showLoggedInView(email);
        }, 500);
        
        // Fetch billing status after login
        await updateBillingStatus(data.access_token);
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
// ANALYZE PREVIEW FEATURE
// ============================================================================

/**
 * Generic insights for preview (matches backend)
 */
const mockInsights = [
  "Profile shows professional experience relevant to B2B outreach",
  "Active LinkedIn presence with industry connections",
  "Career progression indicates decision-making authority",
  "Engagement patterns suggest openness to business opportunities",
  "Profile completeness indicates professional communication preference",
  "Industry alignment with typical target market profiles"
];

/**
 * Handle analyze button click
 */
async function handleAnalyze() {
  showStatus("Getting active tab...", "info");
  analyzeButton.disabled = true;

  try {
    // Query active tab
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    const activeTab = tabs[0];

    if (!activeTab || !activeTab.url) {
      showStatus("Could not access active tab", "error");
      analyzeButton.disabled = false;
      return;
    }

    // Validate LinkedIn URL
    const linkedInProfileRegex = /https:\/\/(www\.)?linkedin\.com\/in\/[a-zA-Z0-9\-]+/;
    if (!linkedInProfileRegex.test(activeTab.url)) {
      showStatus("❌ Please open a LinkedIn profile (linkedin.com/in/...)", "error");
      analyzeButton.disabled = false;
      return;
    }

    // Get authentication token
    const result = await chrome.storage.local.get(['access_token']);
    if (!result.access_token) {
      showStatus("Please login first", "error");
      analyzeButton.disabled = false;
      return;
    }

    // Check billing status and credits before making the call
    showStatus("Checking credits...", "info");
    const billingStatus = await fetchBillingStatus(result.access_token);
    
    if (!billingStatus.can_analyze) {
      analyzeButton.disabled = false;
      if (billingStatus.plan === 'free') {
        showLimitModal();
      } else {
        showStatus("⚠️ You've reached your monthly limit. Your credits reset on the 1st.", "error");
      }
      return;
    }

    // Extract profile data from the page
    showStatus("Extracting profile data...", "info");
    const profileData = await extractProfileData(activeTab.id);
    
    if (!profileData || Object.keys(profileData).length === 0) {
      showStatus("❌ Could not extract profile data. Make sure you're on a LinkedIn profile page.", "error");
      analyzeButton.disabled = false;
      return;
    }

    // Call the real API endpoint
    showStatus("Analyzing profile with AI...", "info");
    const response = await fetch(`${API_CONFIG.baseUrl}/api/v1/analyze/linkedin`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${result.access_token}`
      },
      body: JSON.stringify({
        profile_extract: profileData,
        profile_url: activeTab.url
      })
    });

    if (response.status === 429) {
      // User hit monthly limit - 1 credit will be deducted when limit is reached
      analyzeButton.disabled = false;
      showLimitModal();
      return;
    }

    if (response.status === 403) {
      // No active subscription or credits
      analyzeButton.disabled = false;
      showLimitModal();
      return;
    }

    if (!response.ok) {
      // Generic error - don't show technical details
      const errorData = await response.json().catch(() => ({}));
      const errorMsg = errorData.detail || "Unable to analyze profile. Please try again.";
      showStatus(`❌ ${errorMsg}`, "error");
      analyzeButton.disabled = false;
      return;
    }

    const data = await response.json();
    
    // Check if response is in preview mode (no credits used)
    if (data.preview) {
      // Preview mode - show upgrade prompt
      analyzeButton.disabled = false;
      showLimitModal();
      return;
    }

    // Success! 1 credit was deducted by the backend
    // Display real results
    showStatus("", "");
    displayAnalysisResults(data);
    
    // Refresh billing status to update credits display
    await refreshBillingStatus();
    
    analyzeButton.disabled = false;
  } catch (error) {
    console.error("Analyze error:", error);
    // Don't show technical errors to user
    showStatus("Unable to analyze profile. Please try again.", "error");
    analyzeButton.disabled = false;
  }
}

/**
 * Extract profile data from LinkedIn page using content script
 */
async function extractProfileData(tabId) {
  try {
    const response = await chrome.tabs.sendMessage(tabId, { action: "extractProfile" });
    if (response && response.success) {
      return response.data;
    }
    return null;
  } catch (error) {
    console.error("Failed to extract profile data:", error);
    return null;
  }
}

/**
 * Display real analysis results from API
 */
function displayAnalysisResults(data) {
  // Extract UI data from response
  const ui = data.ui || {};
  const qualification = data.qualification || {};
  
  // Show contact recommendation
  const shouldContact = ui.should_contact;
  const priority = ui.priority || "medium";
  const score = ui.score || 0;
  
  // Render star rating based on score (convert 0-100 to 1-5 stars)
  const starCount = Math.round((score / 100) * 5);
  renderStars(starCount);
  
  // Display key insights
  const insights = [];
  
  if (ui.reasoning) {
    insights.push(ui.reasoning);
  }
  
  if (ui.key_points && Array.isArray(ui.key_points)) {
    insights.push(...ui.key_points);
  }
  
  if (ui.suggested_approach) {
    insights.push(`💡 Suggested approach: ${ui.suggested_approach}`);
  }
  
  if (ui.red_flags && ui.red_flags.length > 0) {
    insights.push(`⚠️ Red flags: ${ui.red_flags.join(", ")}`);
  }
  
  // Render insights list
  insightsList.innerHTML = "";
  insights.slice(0, 5).forEach((insight) => {
    const li = document.createElement("li");
    li.textContent = insight;
    insightsList.appendChild(li);
  });
  
  // Show contact recommendation badge
  if (shouldContact) {
    const badge = document.createElement("div");
    badge.className = "success-badge";
    badge.style.marginBottom = "12px";
    const priorityEmoji = priority === "high" ? "🔥" : priority === "medium" ? "✅" : "👍";
    badge.textContent = `${priorityEmoji} Recommended Contact (${priority} priority)`;
    resultsContainer.insertBefore(badge, resultsContainer.firstChild);
  }
  
  // Show results, hide analyze button
  resultsContainer.style.display = "block";
  analyzeButton.style.display = "none";
}

/**
 * Refresh billing status to update credits display
 */
async function refreshBillingStatus() {
  const result = await chrome.storage.local.get(['access_token']);
  if (result.access_token) {
    const billingStatus = await fetchBillingStatus(result.access_token);
    if (billingStatus) {
      updateUIWithBillingStatus(billingStatus);
    }
  }
}

/**
 * Generate and display preview results
 */
function generatePreviewResults() {
  // Generate random score (3-5 stars)
  const score = Math.floor(Math.random() * 3) + 3; // 3, 4, or 5

  // Render stars
  renderStars(score);

  // Shuffle and pick 3 random insights
  const shuffled = [...mockInsights].sort(() => 0.5 - Math.random());
  const selectedInsights = shuffled.slice(0, 3);

  // Render insights
  insightsList.innerHTML = "";
  selectedInsights.forEach((insight) => {
    const li = document.createElement("li");
    li.textContent = insight;
    insightsList.appendChild(li);
  });

  // Show results, hide analyze button
  resultsContainer.style.display = "block";
  analyzeButton.style.display = "none";
}

/**
 * Render star rating
 */
function renderStars(count) {
  starRating.innerHTML = "";
  for (let i = 0; i < 5; i++) {
    const star = document.createElement("span");
    star.className = "star";
    star.textContent = i < count ? "★" : "☆";
    starRating.appendChild(star);
  }
}

/**
 * Hide results and show analyze button again
 */
function hideResults() {
  resultsContainer.style.display = "none";
  analyzeButton.style.display = "block";
  clearStatus();
}

/**
 * Handle View Pricing button click
 */
function handleViewPricing() {
  // Open pricing.html in a new tab
  const pricingUrl = chrome.runtime.getURL("pricing.html");
  chrome.tabs.create({ url: pricingUrl });
}

/**
 * Show limit reached modal
 */
function showLimitModal() {
  limitModal.style.display = "flex";
}

/**
 * Close limit reached modal
 */
function closeLimitModal() {
  limitModal.style.display = "none";
}

/**
 * Handle Upgrade Plan button click
 */
function handleUpgrade() {
  const pricingUrl = chrome.runtime.getURL("pricing.html");
  chrome.tabs.create({ url: pricingUrl });
  closeLimitModal();
}

/**
 * Handle View Usage button click
 */
function handleViewUsage() {
  chrome.storage.local.get(['access_token'], (result) => {
    if (!result.access_token) {
      showStatus("Please login first", "error");
      closeLimitModal();
      return;
    }

    // Open dashboard with usage tab
    const backendUrl = API_CONFIG.baseUrl;
    const usageUrl = `${backendUrl}/dashboard#usage`;
    
    chrome.tabs.create({ url: usageUrl }, () => {
      closeLimitModal();
    });
  });
}

/**
 * Show feedback section
 */
function showFeedbackSection() {
  feedbackSection.style.display = "block";
  showFeedbackButton.style.display = "none";
  feedbackTextarea.value = "";
  feedbackTextarea.focus();
}

/**
 * Hide feedback section
 */
function hideFeedbackSection() {
  feedbackSection.style.display = "none";
  showFeedbackButton.style.display = "block";
  clearFeedbackStatus();
}

/**
 * Handle submit feedback
 */
async function handleSubmitFeedback() {
  const message = feedbackTextarea.value.trim();
  
  if (!message || message.length < 5) {
    showFeedbackStatus("Please write at least 5 characters", "error");
    return;
  }

  chrome.storage.local.get(['access_token'], async (result) => {
    if (!result.access_token) {
      showFeedbackStatus("Please login first", "error");
      return;
    }

    try {
      submitFeedbackButton.disabled = true;
      submitFeedbackButton.textContent = "Sending...";
      
      const response = await fetch(
        `${API_CONFIG.baseUrl}/feedback/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${result.access_token}`
          },
          body: JSON.stringify({ message })
        }
      );

      if (!response.ok) {
        throw new Error("Failed to submit feedback");
      }

      const data = await response.json();
      showFeedbackStatus(data.message || "Thank you for your feedback!", "success");
      feedbackTextarea.value = "";
      
      // Hide feedback section after 2 seconds
      setTimeout(() => {
        hideFeedbackSection();
      }, 2000);
      
    } catch (error) {
      console.error("Feedback error:", error);
      showFeedbackStatus("Failed to send feedback. Please try again.", "error");
    } finally {
      submitFeedbackButton.disabled = false;
      submitFeedbackButton.textContent = "Send Feedback";
    }
  });
}

/**
 * Show feedback status message
 */
function showFeedbackStatus(message, type) {
  feedbackStatus.textContent = message;
  feedbackStatus.className = `status visible ${type}`;
}

/**
 * Clear feedback status message
 */
function clearFeedbackStatus() {
  feedbackStatus.textContent = "";
  feedbackStatus.className = "status";
}

// Initialize on popup load
document.addEventListener("DOMContentLoaded", () => {
  checkLoginStatus();
  setupEventListeners();
});
