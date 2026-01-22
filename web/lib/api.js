/**
 * Validate email format
 */
export function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

/**
 * Get stored JWT token from localStorage
 */
export function getStoredToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("authToken") || null;
}

/**
 * Store JWT token in localStorage
 */
export function storeToken(token) {
  if (typeof window === "undefined") return;
  localStorage.setItem("authToken", token);
}

/**
 * Clear stored JWT token
 */
export function clearToken() {
  if (typeof window === "undefined") return;
  localStorage.removeItem("authToken");
}

/**
 * Login with email (POST /auth/login)
 * Returns: { access_token, token_type }
 */
export async function login(email) {
  const response = await fetch(`${API_URL}/auth/login`, {
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

  storeToken(data.access_token);
  return data;
}

/**
 * Make authenticated API request with JWT token
 */
export async function authenticatedFetch(endpoint, options = {}) {
  const token = getStoredToken();

  if (!token) {
    throw new Error("Not authenticated. Please login first.");
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  // Handle 401 Unauthorized (token expired)
  if (response.status === 401) {
    clearToken();
    throw new Error("Session expired. Please login again.");
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "API error" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Save ICP configuration (POST /user/icp or similar endpoint)
 * Assuming we'll use a PUT endpoint to update user's ICP
 */
export async function saveICP(icpConfig) {
  return authenticatedFetch("/user/icp", {
    method: "PUT",
    body: JSON.stringify(icpConfig),
  });
}

/**
 * Get user profile (to verify ICP is saved)
 */
export async function getUserProfile() {
  return authenticatedFetch("/user/profile");
}
