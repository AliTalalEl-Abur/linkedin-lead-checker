/**
 * Popup Script: Authentication Flow
 * - Login with email/password
 * - Store token securely in chrome.storage.local
 * - Persist login state on popup load
 */

console.log("popup.js loaded - Extension initializing");

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
const analyzeButton = document.getElementById("analyzeButton");
const resultsContainer = document.getElementById("resultsContainer");
const backButton = document.getElementById("backButton");
const starRating = document.getElementById("starRating");
const insightsList = document.getElementById("insightsList");

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
  analyzeButton.addEventListener("click", handleAnalyze);
  backButton.addEventListener("click", hideResults);
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
// ANALYZE PREVIEW FEATURE
// ============================================================================

/**
 * Mock insights for preview
 */
const mockInsights = [
  "Strong career progression in tech leadership",
  "Experience aligns well with B2B SaaS market",
  "Active in professional community with 500+ connections",
  "Recent role change indicates growth mindset",
  "Well-established network in target industry"
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

    // Generate preview results
    showStatus("", "");
    generatePreviewResults();
    analyzeButton.disabled = false;
  } catch (error) {
    console.error("Analyze error:", error);
    showStatus("Error accessing active tab", "error");
    analyzeButton.disabled = false;
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
// Initialize on popup load
document.addEventListener("DOMContentLoaded", () => {
  checkLoginStatus();
  setupEventListeners();
});
