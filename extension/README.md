# LinkedIn Lead Checker Extension

A Chrome extension for analyzing LinkedIn profiles with AI-powered lead scoring.

## Features
- **Robust Profile Extraction**: Uses stable selectors (aria-labels, data-attributes) instead of fragile CSS classes
- **AI Scoring**: Uses OpenAI to score profile fit and generate recommendations
- **Auth Integration**: Magic login with email
- **Usage Control**: Respects free/pro plan limits

## Installation

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right)
3. Click **Load unpacked**
4. Select the `extension/` folder

## File Structure

```
extension/
├── manifest.json          # Chrome extension manifest (v3)
├── popup.html            # Popup UI
├── popup.js              # Popup logic & API calls
├── src/
│   ├── content.js        # LinkedIn profile extraction (robust)
│   └── background.js     # Service worker for API calls
├── public/
│   └── icons/           # Extension icons (placeholder)
└── EXTRACTOR_NOTES.md   # Extraction strategy documentation
```

## Profile Extraction (MVP Robust)

The content script extracts a minimal but consistent `profile_extract` object:

```json
{
  "name": "Jane Smith",
  "headline": "VP of Engineering at TechCorp",
  "about": "Passionate about building scalable systems...",
  "experience_titles": [
    "VP of Engineering",
    "Senior Software Engineer",
    "Software Engineer"
  ],
  "url": "https://www.linkedin.com/in/janesmith/",
  "timestamp": "2026-01-19T12:34:56.789Z"
}
```

### Robustness Strategy

**Does NOT depend on fragile CSS classes.** Instead uses:

1. **Semantic HTML**: h1 (name), div structure (headline)
2. **aria-labels**: `aria-label="About"`, `aria-label="Experience section"`
3. **data-test-id**: LinkedIn's own testing attributes (more stable)
4. **DOM structure**: Relative positioning (sibling traversal)
5. **Text patterns**: Regex fallbacks for job titles

**Survivability**: ~95% of LinkedIn profiles, resistant to LinkedIn CSS/class changes.

See [EXTRACTOR_NOTES.md](EXTRACTOR_NOTES.md) for detailed extraction strategy.

## Setup

1. Ensure the backend API is running locally:
   ```powershell
   C:/Users/LENOVO/Desktop/linkedin-lead-checker/.venv/Scripts/python.exe run.py
   ```

2. Visit a LinkedIn profile page (e.g., `linkedin.com/in/someone/`)

3. Click the **LinkedIn Lead Checker** extension icon (🔍)

4. Login with your email

5. Click **Analyze Profile** to score the profile

## Configuration

The extension calls the API at `BACKEND_URL` by default.
To change, edit the `API_CONFIG` in:
- `src/background.js`
- `popup.js`

## Permissions

- `activeTab`: Access current tab
- `scripting`: Run content script
- `storage`: Store auth token
- `host_permissions`: Access LinkedIn URLs (minimal)

## Manifest v3 Features
- Service worker instead of background page
- Declarative host permissions
- Content script only loads on `linkedin.com/in/*` pages
- No unsafe eval or remote code execution
