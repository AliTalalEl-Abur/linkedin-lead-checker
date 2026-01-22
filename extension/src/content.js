/**
 * Content Script: Runs on LinkedIn profile pages (linkedin.com/in/*)
 * Robust profile extraction using stable selectors (aria-labels, data-attributes, DOM structure)
 * Does NOT depend on fragile CSS classes
 */

/**
 * Safely extract text from an element
 */
function safeText(el) {
  if (!el) return null;
  const text = el.textContent.trim();
  return text.length > 0 ? text : null;
}

/**
 * Extract profile data from LinkedIn profile page
 * Returns a minimal, consistent profile_extract object
 */
function extractProfileData() {
  const profile = {
    // Core fields (required)
    name: null,
    headline: null,
    about: null,
    experience_titles: [],
    
    // Metadata
    url: window.location.href,
    timestamp: new Date().toISOString(),
  };

  // ===== 1. Extract Name =====
  // LinkedIn profile page structure: h1 is always the full name
  const nameEl = document.querySelector("h1");
  profile.name = safeText(nameEl);

  // ===== 2. Extract Headline =====
  // Headline is usually the first div after h1, or the next element
  // Look for text that comes right after name
  if (nameEl) {
    let headlineEl = nameEl.nextElementSibling;
    while (headlineEl && headlineEl.tagName !== "DIV") {
      headlineEl = headlineEl.nextElementSibling;
    }
    if (headlineEl) {
      profile.headline = safeText(headlineEl);
    }
  }

  // Fallback: search for headline in common patterns
  if (!profile.headline) {
    const possibleHeadlines = document.querySelectorAll("[data-test-id*='headline'], h2");
    for (const el of possibleHeadlines) {
      const text = safeText(el);
      if (text && text.length < 200 && !text.includes("@")) {
        profile.headline = text;
        break;
      }
    }
  }

  // ===== 3. Extract About Section =====
  // LinkedIn structure: About section has aria-label "About" or contains "About" text
  const aboutLabels = document.querySelectorAll("[aria-label='About']");
  for (const label of aboutLabels) {
    // Navigate up to find the section, then find the text content
    let section = label.closest("section") || label.parentElement.parentElement;
    if (section) {
      const textEls = section.querySelectorAll("p, div");
      for (const el of textEls) {
        const text = safeText(el);
        if (text && text.length > 50 && !text.includes("See more")) {
          profile.about = text.substring(0, 500); // Limit to 500 chars
          break;
        }
      }
      if (profile.about) break;
    }
  }

  // Fallback: search for About text in the page
  if (!profile.about) {
    const allText = document.body.innerText;
    const aboutMatch = allText.match(/About[\s\S]{0,600}?(?=Experience|Skills|Education|$)/i);
    if (aboutMatch) {
      const cleanText = aboutMatch[0]
        .replace(/^About\s*/i, "")
        .trim()
        .substring(0, 500);
      if (cleanText.length > 50) {
        profile.about = cleanText;
      }
    }
  }

  // ===== 4. Extract Experience Titles =====
  // LinkedIn structure: Experience items are usually in sections with title elements
  const experienceTitles = new Set();

  // Method 1: Look for experience section and extract job titles
  const experienceLabels = document.querySelectorAll("[aria-label='Experience section']");
  for (const label of experienceLabels) {
    let section = label.closest("section") || label.parentElement.parentElement;
    if (section) {
      // Job titles are in headings or strong elements within experience items
      const titles = section.querySelectorAll("h3, [data-test-id*='title'], strong");
      for (const titleEl of titles) {
        const title = safeText(titleEl);
        if (title && title.length > 2 && title.length < 100 && !title.includes("See more")) {
          experienceTitles.add(title);
        }
      }
    }
  }

  // Method 2: Look for experience items via data-test-id (more robust)
  const expItems = document.querySelectorAll("[data-test-id*='experience-item'], [data-test-id*='profile-experience']");
  for (const item of expItems) {
    // First heading in the item is usually the job title
    const titleEl = item.querySelector("h3, h4");
    if (titleEl) {
      const title = safeText(titleEl);
      if (title && title.length > 2 && title.length < 100) {
        experienceTitles.add(title);
      }
    }
  }

  // Method 3: Fallback - search for common job title patterns in the page text
  if (experienceTitles.size === 0) {
    const pageText = document.body.innerText;
    const jobTitlePatterns = [
      /(?:Manager|Director|VP|Engineer|Developer|Designer|Product|Lead|Head|Chief|Officer|Analyst|Consultant|Specialist)\s+(?:of|for)?[^(\n]{0,80}/gi,
    ];
    for (const pattern of jobTitlePatterns) {
      const matches = pageText.match(pattern);
      if (matches) {
        matches.forEach((title) => {
          const clean = title.trim().substring(0, 80);
          if (clean.length > 2) {
            experienceTitles.add(clean);
          }
        });
      }
    }
  }

  profile.experience_titles = Array.from(experienceTitles).slice(0, 10); // Limit to 10 titles

  return profile;
}

/**
 * Verify this is a LinkedIn profile page
 */
function isLinkedInProfilePage() {
  return /linkedin\.com\/in\//.test(window.location.href);
}

// ===== Message Listener =====
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "extractProfile") {
    if (!isLinkedInProfilePage()) {
      sendResponse({ success: false, error: "Not a LinkedIn profile page" });
      return;
    }
    const profileData = extractProfileData();
    sendResponse({ success: true, data: profileData });
  }
});

// ===== Auto-notify background script when page loads =====
if (isLinkedInProfilePage()) {
  const profileData = extractProfileData();
  chrome.runtime.sendMessage({
    action: "profileLoaded",
    data: profileData,
  }).catch(() => {
    // Background script not ready; silently fail
  });
}
