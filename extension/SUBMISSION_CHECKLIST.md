# Chrome Web Store Submission Checklist

## ✅ Pre-Submission Preparation

### 1. Manifest.json Review
- [x] Manifest version 3 (latest)
- [x] Clear, honest description (132 chars max)
- [x] Minimal permissions (only `activeTab`, `storage`)
- [x] Host permissions limited to `linkedin.com/in/*` (profile pages only)
- [x] Content scripts declared explicitly
- [x] No unnecessary permissions (removed `scripting`)
- [x] Icons properly referenced (16, 48, 128)

### 2. Code Review
- [x] No obfuscated code
- [x] No automatic/background scraping
- [x] User-initiated data collection only (click "Analyze")
- [x] Secure authentication (chrome.storage.local)
- [x] Clean error handling
- [x] No prohibited APIs

### 3. Privacy & Compliance
- [x] Privacy Policy written (PRIVACY_POLICY.md)
- [ ] Host privacy policy at public URL (linkedin-lead-checker.vercel.app/privacy)
- [x] Store listing copy prepared (CHROME_STORE_LISTING.md)
- [x] Data usage clearly disclosed
- [x] No data selling
- [x] GDPR compliance statement
- [x] CCPA compliance statement

### 4. Functionality Testing
- [ ] Test login flow
- [ ] Test free preview mode
- [ ] Test paid analysis mode (with subscription)
- [ ] Test limit modal display
- [ ] Test logout flow
- [ ] Test on multiple LinkedIn profiles
- [ ] Test error handling (network errors, invalid tokens)
- [ ] Test with expired subscription

### 5. Assets Creation
#### Required Icons (✓ Have)
- [x] 16x16px (toolbar)
- [x] 48x48px (extension management)
- [x] 128x128px (Chrome Web Store)

#### Store Graphics (Need to Create)
- [ ] 440x280px promotional tile (REQUIRED)
- [ ] 1280x800px screenshots (5 minimum):
  - [ ] Screenshot 1: Popup with analysis results
  - [ ] Screenshot 2: Login interface
  - [ ] Screenshot 3: Free preview display
  - [ ] Screenshot 4: Full AI analysis
  - [ ] Screenshot 5: Pricing/subscription view
- [ ] 920x680px marquee (optional but recommended)

### 6. Store Listing Content
- [x] Short description (105 chars)
- [x] Full description (~2,000 chars)
- [x] Privacy practices disclosure
- [x] Categories selected (Productivity, Social & Communication)
- [x] Keywords/tags identified

### 7. Support Infrastructure
- [ ] Set up support email: support@linkedin-lead-checker.com
- [ ] Set up privacy email: privacy@linkedin-lead-checker.com
- [ ] Create test account for reviewers:
  - Email: reviewer@test.com
  - Password: ChromeReview2024!
  - With sample analyses in history
- [ ] Verify backend API accessible (https://linkedin-lead-checker-api.onrender.com)
- [ ] Verify frontend accessible (https://linkedin-lead-checker.vercel.app)

### 8. Legal & Documentation
- [ ] Host Privacy Policy at: linkedin-lead-checker.vercel.app/privacy
- [ ] Host Terms of Service at: linkedin-lead-checker.vercel.app/terms
- [ ] Create support/FAQ page
- [ ] Verify LinkedIn ToS compliance
- [ ] Prepare reviewer notes document

---

## 📦 Packaging for Submission

### What to Include in ZIP
```
extension/
├── manifest.json          ✓ Updated with minimal permissions
├── popup.html             ✓ Main UI
├── popup.js               ✓ Authentication & analysis logic
├── style.css              ✓ Styling
├── pricing.html           ✓ Pricing view
├── src/
│   ├── background.js      ✓ Minimal service worker
│   └── content.js         ✓ Profile extraction (user-initiated)
└── public/
    ├── icon-16.png        ✓ Toolbar icon
    ├── icon-48.png        ✓ Management icon
    └── icon-128.png       ✓ Store icon
```

### What to EXCLUDE
- ❌ node_modules/
- ❌ .git/
- ❌ .env files
- ❌ README.md (documentation only)
- ❌ test files
- ❌ Development scripts

### Create ZIP Command
```bash
cd extension
zip -r ../linkedin-lead-checker-v1.0.0.zip . -x "*.md" "test_*" "*.txt" ".DS_Store"
```

Or manually:
1. Open extension/ folder
2. Select all files EXCEPT .md, test files
3. Right-click → Send to → Compressed folder
4. Name: linkedin-lead-checker-v1.0.0.zip

---

## 🚀 Submission Steps

### 1. Chrome Web Store Developer Dashboard
- URL: https://chrome.google.com/webstore/devcenter
- One-time $5 developer registration fee (if first extension)

### 2. Upload Extension
- Click "New Item"
- Upload ZIP file
- Wait for automated checks to complete

### 3. Store Listing
#### Item Details
- **Product name**: LinkedIn Lead Checker
- **Summary**: (105 char description from CHROME_STORE_LISTING.md)
- **Category**: Productivity
- **Language**: English (United States)

#### Detailed Description
- Paste full description from CHROME_STORE_LISTING.md

#### Graphic Assets
- Upload 440x280 promotional tile
- Upload 5 screenshots (1280x800)
- Optional: Upload marquee images

#### Privacy
- **Privacy Policy URL**: https://linkedin-lead-checker.vercel.app/privacy
- **Single Purpose**: Lead qualification on LinkedIn profiles
- **Permission Justification**:
  - `activeTab`: Read profile data when user clicks "Analyze"
  - `storage`: Store authentication token securely
- **Host Permission Justification**: 
  - `linkedin.com/in/*`: Access LinkedIn profile pages for analysis

#### Additional Fields
- **Website**: https://linkedin-lead-checker.vercel.app
- **Support URL**: https://linkedin-lead-checker.vercel.app/support
- **Support Email**: support@linkedin-lead-checker.com

### 4. Privacy Practices
Answer Chrome Store privacy questionnaire:
- **Does this extension handle personal or sensitive user data?** Yes
  - Email addresses (for authentication)
  - Website content (LinkedIn profile data)
- **Is the data being transmitted?** Yes
  - To our secure API for analysis
- **Is the data sold?** No
- **Is the data used for purposes unrelated to the extension's functionality?** No

### 5. Reviewer Notes (Optional but Recommended)
```
Dear Chrome Store Review Team,

Thank you for reviewing LinkedIn Lead Checker.

KEY POINTS:
1. Extension only collects data when user clicks "Analyze" button
2. No automatic or background scraping
3. Free tier provides basic preview, subscription unlocks AI analysis
4. Privacy-first design: minimal data collection, no data selling

TEST CREDENTIALS:
Email: reviewer@test.com
Password: ChromeReview2024!

TESTING STEPS:
1. Install extension
2. Go to any LinkedIn profile (e.g., linkedin.com/in/williamhgates)
3. Click extension icon
4. Log in with test credentials
5. Click "Analyze" to see free preview
6. Full AI analysis requires subscription (visible in UI)

BACKEND: https://linkedin-lead-checker-api.onrender.com
FRONTEND: https://linkedin-lead-checker.vercel.app
PRIVACY POLICY: https://linkedin-lead-checker.vercel.app/privacy

Feel free to reach out at support@linkedin-lead-checker.com for any questions.
```

### 6. Submit for Review
- Click "Submit for Review"
- Wait 1-3 business days typically
- Monitor email for reviewer feedback

---

## 🔍 Common Review Issues & Solutions

### Issue: "Excessive Permissions"
**Solution**: We've minimized to only `activeTab` and `storage`. Removed `scripting` permission by declaring content_scripts in manifest.

### Issue: "Privacy Policy Insufficient"
**Solution**: Our privacy policy (PRIVACY_POLICY.md) covers:
- What data we collect
- How we use it
- User rights (GDPR, CCPA)
- No data selling statement
- Third-party services disclosed

### Issue: "Single Purpose Unclear"
**Solution**: Clear description: "Preview LinkedIn profile fit before reaching out. Free basic info, full AI analysis with subscription."

### Issue: "Prohibited Data Collection"
**Solution**: Extension only collects data when user explicitly clicks "Analyze". No background scraping.

---

## 📊 Post-Submission Monitoring

### Review Status
- Check dashboard daily for status updates
- Respond to reviewer questions within 24 hours
- Be prepared to make small adjustments

### After Approval
- [ ] Test live version from Chrome Web Store
- [ ] Update website with Chrome Store link
- [ ] Announce launch
- [ ] Monitor reviews and ratings
- [ ] Set up crash/error reporting

---

## 🔄 Future Updates

### Version Updates
- Increment version in manifest.json
- Create changelog
- Re-submit for review (faster than initial review)

### Best Practices
- Test thoroughly before each update
- Keep permissions minimal
- Document all changes
- Respond to user reviews

---

## 📞 Important Contacts

**Chrome Store Support**: 
- Forum: https://support.google.com/chrome_webstore/community

**Your Support Channels**:
- Email: support@linkedin-lead-checker.com
- Privacy: privacy@linkedin-lead-checker.com
- Website: https://linkedin-lead-checker.vercel.app

---

## ⚠️ DO NOT PUBLISH YET

Complete these tasks FIRST:
1. ✅ Privacy policy hosted at public URL
2. ⬜ Create promotional graphics (440x280)
3. ⬜ Take 5 screenshots
4. ⬜ Set up support email
5. ⬜ Create reviewer test account
6. ⬜ Final functionality testing
7. ⬜ Team review of store listing

**Once all checked, you're ready to submit!**
