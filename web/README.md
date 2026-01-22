# LinkedIn Lead Checker Web App

A Next.js web application for user authentication, ICP configuration, and profile management.

## Features

- **Login**: Magic email login (creates account if first time)
- **ICP Onboarding**: Configure ideal customer profile:
  - Value proposition / offer
  - Target job titles / seniority levels
  - Roles to avoid
  - Target industries
  - Company size range
- **Dashboard**: View setup status and next steps
- **No external dependencies**: Pure Next.js with minimal package.json

## Setup

### Prerequisites

- Node.js 18+ installed
- Backend API running on `http://127.0.0.1:8000`

### Installation

```bash
cd web

# Install dependencies
npm install

# Set API URL (optional, defaults to http://127.0.0.1:8000)
export NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

# Start dev server
npm run dev
```

The app will be available at `http://localhost:3000`

## Project Structure

```
web/
├── pages/
│   ├── _app.js              # App wrapper, styles
│   ├── login.js             # Login page
│   ├── onboarding.js        # ICP configuration
│   └── dashboard.js         # Setup complete
├── lib/
│   └── api.js              # API utilities (login, saveICP, etc)
├── styles/
│   ├── globals.css         # Global styles
│   ├── Auth.module.css     # Login/auth styles
│   ├── Onboarding.module.css # Onboarding form styles
│   └── Dashboard.module.css  # Dashboard styles
├── components/            # (future) React components
├── public/               # Static assets
├── package.json
├── next.config.js
└── tsconfig.json
```

## Flow

### User Journey

```
1. User visits http://localhost:3000
   → Redirects to /login (if not authenticated)

2. User enters email and clicks "Login"
   → Calls POST /auth/login with { email }
   → Backend returns { access_token }
   → Token stored in localStorage
   → User redirected to /onboarding

3. User fills ICP form:
   - Value proposition
   - Target roles (multi-select)
   - Roles to avoid (multi-select)
   - Target industries (multi-select)
   - Company size min/max
   → Calls PUT /user/icp with ICP config
   → Backend saves ICP to user record
   → User redirected to /dashboard

4. User sees confirmation and next steps
   → Can edit ICP anytime
   → Can logout and come back later
```

### Authentication

- **Method**: JWT token in localStorage
- **Endpoint**: `POST /auth/login`
- **Storage Key**: `authToken`
- **Authenticated calls**: Include `Authorization: Bearer <token>` header

## API Endpoints Used

```
POST /auth/login
  Body: { email: "user@example.com" }
  Response: { access_token: "...", token_type: "bearer" }

PUT /user/icp
  Headers: { Authorization: "Bearer <token>" }
  Body: {
    target_industries: ["Technology", "SaaS"],
    target_seniority: ["VP", "Director", "Manager"],
    exclude_keywords: ["Intern", "Freelancer"],
    company_size_min: 50,
    company_size_max: 5000
  }
  Response: { success: true, message: "ICP saved" }
```

## Backend Integration

The backend needs to implement:

1. **User model update**: Add endpoint to save/update user's ICP config
   - Currently assumes `PUT /user/icp` endpoint
   - Saves `icp_config_json` to User model

2. **Suggested endpoint** (if not already present):
   ```python
   # In app/api/routes/user.py
   @router.put("/icp")
   def update_user_icp(
       icp_config: ICPConfig,
       current_user: User = Depends(get_current_user),
       db: Session = Depends(get_db),
   ):
       current_user.icp_config_json = icp_config.model_dump()
       db.commit()
       return { "message": "ICP saved successfully" }
   ```

## Styling

- Pure CSS Modules (no Tailwind, no CSS-in-JS)
- LinkedIn Blue (#0a66c2) as primary color
- Mobile responsive
- Clean, minimal design

## Environment Variables

```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000  # Backend API URL
```

## Next Steps (Future)

- [ ] Payment integration (Stripe)
- [ ] Usage analytics dashboard
- [ ] Team management
- [ ] Custom ICP templates
- [ ] Export leads
