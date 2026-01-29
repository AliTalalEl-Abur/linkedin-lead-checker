/**
 * Dashboard JavaScript - Client-side logic for web dashboard
 */

const API_BASE = window.RUNTIME_CONFIG && window.RUNTIME_CONFIG.API_URL;

const elements = {
  authSection: document.getElementById('authSection'),
  dashboardSection: document.getElementById('dashboardSection'),
  authStatus: document.getElementById('authStatus'),
  dashStatus: document.getElementById('dashStatus'),
  
  emailInput: document.getElementById('emailInput'),
  loginBtn: document.getElementById('loginBtn'),
  logoutBtn: document.getElementById('logoutBtn'),
  
  userEmail: document.getElementById('userEmail'),
  userPlan: document.getElementById('userPlan'),
  userCreated: document.getElementById('userCreated'),
  
  usageUsed: document.getElementById('usageUsed'),
  usageRemaining: document.getElementById('usageRemaining'),
  usageProgress: document.getElementById('usageProgress'),
  usageNote: document.getElementById('usageNote'),
  
  upgradeCTA: document.getElementById('upgradeCTA'),
  upgradeButtons: document.querySelectorAll('.upgrade-btn'),
  
  icpForm: document.getElementById('icpForm'),
  targetIndustries: document.getElementById('targetIndustries'),
  targetSeniority: document.getElementById('targetSeniority'),
  companySizeMin: document.getElementById('companySizeMin'),
  companySizeMax: document.getElementById('companySizeMax'),
  requiredSkills: document.getElementById('requiredSkills'),
  minYearsExp: document.getElementById('minYearsExp'),
};

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', async () => {
  if (!API_BASE) {
    showAuthSection();
    showAuthStatus('API URL is not configured. Please contact support.', 'error');
    return;
  }

  const token = getToken();
  
  if (token) {
    await loadDashboard();
  } else {
    showAuthSection();
  }
});

// ============================================================================
// AUTHENTICATION
// ============================================================================

elements.loginBtn.addEventListener('click', async () => {
  const email = elements.emailInput.value.trim();
  
  if (!email || !isValidEmail(email)) {
    showAuthStatus('Please enter a valid email address', 'error');
    return;
  }
  
  elements.loginBtn.disabled = true;
  elements.loginBtn.textContent = 'Logging in...';
  
  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail);
    }
    
    const data = await response.json();
    setToken(data.access_token);
    
    showAuthStatus('✅ Login successful! Redirecting...', 'success');
    elements.emailInput.value = '';
    
    setTimeout(async () => {
      await loadDashboard();
    }, 500);
  } catch (error) {
    console.error('Login error:', error);
    showAuthStatus(`❌ Login failed: ${error.message}`, 'error');
    elements.loginBtn.disabled = false;
    elements.loginBtn.textContent = 'Login with Email';
  }
});

elements.emailInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    elements.loginBtn.click();
  }
});

elements.logoutBtn.addEventListener('click', () => {
  clearToken();
  showAuthSection();
  showAuthStatus('Logged out successfully', 'info');
});

// ============================================================================
// DASHBOARD
// ============================================================================

async function loadDashboard() {
  const token = getToken();
  
  if (!token) {
    showAuthSection();
    return;
  }
  
  try {
    // Fetch user data
    const response = await fetch(`${API_BASE}/user`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    
    if (response.status === 401) {
      clearToken();
      showAuthSection();
      showAuthStatus('Session expired. Please login again.', 'error');
      return;
    }
    
    if (!response.ok) {
      throw new Error('Failed to load user data');
    }
    
    const userData = await response.json();
    
    // Show dashboard
    showDashboard();
    
    // Populate user info
    elements.userEmail.textContent = userData.email;
    elements.userPlan.textContent = userData.plan.toUpperCase();
    elements.userPlan.className = `plan-badge plan-${userData.plan}`;
    
    const createdDate = new Date(userData.created_at);
    elements.userCreated.textContent = createdDate.toLocaleDateString();
    
    // Populate usage stats
    const usage = userData.usage;
    elements.usageUsed.textContent = usage.used;
    elements.usageRemaining.textContent = usage.remaining;
    
    const usagePercent = (usage.used / usage.limit) * 100;
    elements.usageProgress.style.width = `${Math.min(usagePercent, 100)}%`;
    
    // Show/hide upgrade CTA (only show for FREE)
    if (userData.plan === 'free') {
      elements.upgradeCTA.classList.remove('hidden');
    } else {
      elements.upgradeCTA.classList.add('hidden');
    }
    
    // Usage note per plan
    if (elements.usageNote) {
      if (userData.plan === 'free') {
        elements.usageNote.textContent = 'Lifetime limit: 3 free lead checks (no reset). No credit card.';
      } else if (userData.plan === 'pro') {
        elements.usageNote.textContent = 'Fair use: 100 analyses per week. Resets every Monday.';
      } else if (userData.plan === 'team') {
        elements.usageNote.textContent = 'Fair use: 300 analyses per week (team). Resets every Monday.';
      } else {
        elements.usageNote.textContent = '';
      }
    }
    
    // Populate ICP form
    if (userData.icp_config) {
      populateICPForm(userData.icp_config);
    }
    
  } catch (error) {
    console.error('Dashboard load error:', error);
    showDashStatus(`❌ Failed to load dashboard: ${error.message}`, 'error');
  }
}

function populateICPForm(icp) {
  if (icp.target_industries) {
    elements.targetIndustries.value = icp.target_industries.join(', ');
  }
  if (icp.target_seniority) {
    elements.targetSeniority.value = icp.target_seniority.join(', ');
  }
  if (icp.company_size_min !== undefined) {
    elements.companySizeMin.value = icp.company_size_min;
  }
  if (icp.company_size_max !== undefined) {
    elements.companySizeMax.value = icp.company_size_max;
  }
  if (icp.required_skills) {
    elements.requiredSkills.value = icp.required_skills.join(', ');
  }
  if (icp.min_years_experience !== undefined) {
    elements.minYearsExp.value = icp.min_years_experience;
  }
}

// ============================================================================
// ICP FORM
// ============================================================================

elements.icpForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const token = getToken();
  if (!token) {
    showDashStatus('Not authenticated', 'error');
    return;
  }
  
    const icpConfig = {
    target_industries: parseList(elements.targetIndustries.value),
    target_seniority: parseList(elements.targetSeniority.value),
    company_size_min: parseInt(elements.companySizeMin.value) || 0,
    company_size_max: parseInt(elements.companySizeMax.value) || 1000000,
    required_skills: parseList(elements.requiredSkills.value),
    min_years_experience: parseInt(elements.minYearsExp.value) || 0,
    target_locations: null,
    exclude_keywords: null,
  };
  
  try {
    const response = await fetch(`${API_BASE}/user/icp`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(icpConfig),
    });
    
    if (!response.ok) {
      throw new Error('Failed to save ICP configuration');
    }
    
    showDashStatus('✅ ICP configuration saved successfully!', 'success');
    
    setTimeout(() => {
      elements.dashStatus.classList.remove('visible');
    }, 3000);
  } catch (error) {
    console.error('ICP save error:', error);
    showDashStatus(`❌ Failed to save: ${error.message}`, 'error');
  }
});

// ============================================================================
// UPGRADE
// ============================================================================
// UPGRADE (Pro / Team)
if (elements.upgradeButtons && elements.upgradeButtons.length) {
  elements.upgradeButtons.forEach((btn) => {
    btn.addEventListener('click', async () => {
      const plan = btn.dataset.plan || 'pro';
      const token = getToken();
      if (!token) {
        showDashStatus('Please login first', 'error');
        return;
      }
      
      btn.disabled = true;
      const original = btn.textContent;
      btn.textContent = 'Creating checkout...';
      
      try {
        const response = await fetch(`${API_BASE}/billing/checkout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            return_url: `${(window.RUNTIME_CONFIG && window.RUNTIME_CONFIG.SITE_URL) || ''}/billing-return.html?session_id={CHECKOUT_SESSION_ID}`,
            plan,
          }),
        });
        
        if (!response.ok) {
          throw new Error('Failed to create checkout session');
        }
        
        const data = await response.json();
        
        // Redirect to Stripe Checkout
        window.location.href = data.url;
      } catch (error) {
        console.error('Upgrade error:', error);
        showDashStatus(`❌ Failed to start upgrade: ${error.message}`, 'error');
      } finally {
        btn.disabled = false;
        btn.textContent = original;
      }
    });
  });
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function showAuthSection() {
  elements.authSection.classList.remove('hidden');
  elements.dashboardSection.classList.add('hidden');
}

function showDashboard() {
  elements.authSection.classList.add('hidden');
  elements.dashboardSection.classList.remove('hidden');
}

function showAuthStatus(message, type) {
  elements.authStatus.textContent = message;
  elements.authStatus.className = `status ${type} visible`;
}

function showDashStatus(message, type) {
  elements.dashStatus.textContent = message;
  elements.dashStatus.className = `status ${type} visible`;
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function parseList(value) {
  if (!value || !value.trim()) return null;
  return value.split(',').map(s => s.trim()).filter(s => s.length > 0);
}

// ============================================================================
// TOKEN MANAGEMENT
// ============================================================================

function getToken() {
  return localStorage.getItem('authToken');
}

function setToken(token) {
  localStorage.setItem('authToken', token);
}

function clearToken() {
  localStorage.removeItem('authToken');
}
