# LinkedIn Lead Checker - Chrome Extension

## Overview
A Chrome Extension (Manifest V3) for authenticating with the LinkedIn Lead Checker API. This extension focuses solely on the authentication flow, storing JWT tokens securely, and persisting login state.

## Tech Stack
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Architecture**: Chrome Extension MV3
- **Storage**: `chrome.storage.local` for secure token persistence
- **API**: RESTful backend at `https://linkedin-lead-checker-api.onrender.com`

## Features

### ✅ Authentication
- Email + password login
- Secure token storage via `chrome.storage.local`
- Login persistence across popup sessions
- Logout functionality

### ✅ UI States
- **Login Form**: Email/password inputs with login button
- **Logged In**: Display user email and logout button
- **Status Messages**: Info, success, and error messages with appropriate styling

### ✅ API Integration
- POST `/auth/login` endpoint
- Automatic user creation on first login
- Error handling with user-friendly messages
- Loading states during authentication

## File Structure

```
extension/
├── manifest.json          # MV3 configuration
├── popup.html             # Popup UI structure
├── popup.js               # Authentication logic
├── style.css              # Popup styling
├── src/
│   └── background.js      # Service worker (minimal)
└── public/
    └── icon-*.png         # Extension icons
```

## Installation

### For Development
1. Clone the repository
2. Open `chrome://extensions/` in Chrome
3. Enable "Developer mode" (top right)
4. Click "Load unpacked"
5. Select the `extension/` folder

## Usage

### Login Flow
1. Click the extension icon
2. Enter your email address
3. Enter your password
4. Click "Login"
5. Token is automatically stored and UI transitions to logged-in state

### Logout Flow
1. Click the extension icon (if already logged in)
2. Click "Logout"
3. Token is cleared from storage

## API Endpoints

### Login
```http
POST https://linkedin-lead-checker-api.onrender.com/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200 OK)**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Storage
Tokens are stored in `chrome.storage.local`:
```javascript
{
  "access_token": "JWT_TOKEN_HERE",
  "email": "user@example.com"
}
```

## Permissions
- `storage`: Access to `chrome.storage.local` API
- `activeTab`: Detect active tab context
- `scripting`: Future script injection (reserved for analysis features)
- `https://www.linkedin.com/*`: Host permission for LinkedIn access

## Future Extensions
This extension is designed to be extended with:
- Profile extraction from LinkedIn pages
- Analysis API calls
- Results display
- Plan management (Free/Pro/Team)

## Development Notes
- No external frameworks used (Vanilla JS only)
- Responsive design for different popup sizes
- CORS requests to production API
- Secure token storage (not in `localStorage`)
- Clean separation of concerns (HTML/CSS/JS)

## Security
- Tokens stored in `chrome.storage.local` (not accessible to websites)
- No sensitive data in memory longer than necessary
- Secure API communication over HTTPS
- No logging of credentials
