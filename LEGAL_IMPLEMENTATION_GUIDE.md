# Legal Documents Implementation Guide

## 📄 Documents Created

1. **PRIVACY_POLICY.md** - Simple, honest privacy policy
2. **TERMS_OF_SERVICE.md** - Clear terms of service

## 🔗 Where to Link These Documents

### 1. Landing Page (web/)

#### Footer Links
Add to your landing page footer:

```html
<footer>
  <div class="footer-links">
    <a href="/privacy-policy.html">Privacy Policy</a>
    <a href="/terms-of-service.html">Terms of Service</a>
    <a href="mailto:linkedinleadchecker@gmail.com">Contact</a>
  </div>
  <p>&copy; 2026 LinkedIn Lead Checker. All rights reserved.</p>
</footer>
```

#### Sign-Up Form
Add checkbox before registration:

```html
<label>
  <input type="checkbox" required>
  I agree to the <a href="/terms-of-service.html">Terms of Service</a> 
  and <a href="/privacy-policy.html">Privacy Policy</a>
</label>
```

#### Pricing Page
Add note under pricing plans:

```html
<p class="legal-note">
  By subscribing, you agree to our 
  <a href="/terms-of-service.html">Terms of Service</a>. 
  See our <a href="/privacy-policy.html">Privacy Policy</a>.
</p>
```

### 2. Chrome Extension (extension/)

#### Extension Popup (popup.html)
Add to the bottom of popup:

```html
<div class="extension-footer">
  <a href="https://yourwebsite.com/privacy-policy.html" target="_blank">Privacy</a>
  <span>•</span>
  <a href="https://yourwebsite.com/terms-of-service.html" target="_blank">Terms</a>
</div>
```

```css
.extension-footer {
  padding: 8px;
  text-align: center;
  font-size: 11px;
  border-top: 1px solid #eee;
  color: #666;
}

.extension-footer a {
  color: #4A90E2;
  text-decoration: none;
}

.extension-footer a:hover {
  text-decoration: underline;
}
```

#### Chrome Web Store Listing
When publishing, add to description:

```
Privacy Policy: https://yourwebsite.com/privacy-policy.html
Terms of Service: https://yourwebsite.com/terms-of-service.html
```

### 3. Backend API (app/)

#### Sign-Up Endpoint
Add validation to ensure users accept terms:

```python
# app/schemas/auth.py
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    agreed_to_terms: bool  # Add this field
    
    @validator('agreed_to_terms')
    def terms_must_be_accepted(cls, v):
        if not v:
            raise ValueError('You must agree to the Terms of Service')
        return v
```

#### User Model
Store acceptance timestamp:

```python
# app/models/user.py
class User(Base):
    # ... existing fields ...
    terms_accepted_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    privacy_policy_accepted_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
```

### 4. Email Communications

Add footer to all emails:

```html
<footer style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666;">
  <p>LinkedIn Lead Checker</p>
  <p>
    <a href="https://yourwebsite.com/privacy-policy.html">Privacy Policy</a> | 
    <a href="https://yourwebsite.com/terms-of-service.html">Terms of Service</a> | 
    <a href="https://yourwebsite.com/unsubscribe">Unsubscribe</a>
  </p>
</footer>
```

## 📋 Chrome Web Store Requirements

### Privacy Policy Requirements
Google requires a privacy policy URL during extension submission. You need:

1. **Host the policy online** at a permanent URL (e.g., `https://yourwebsite.com/privacy-policy.html`)
2. **Add the URL** to `manifest.json`:

```json
{
  "manifest_version": 3,
  "name": "LinkedIn Lead Checker",
  "privacy_policy": "https://yourwebsite.com/privacy-policy.html"
}
```

### In the Developer Dashboard
When submitting to Chrome Web Store:
- **Privacy practices**: Fill out the data usage disclosure form
- **Privacy Policy URL**: Add your policy URL
- **Justification**: Explain why you need each permission

## 🔒 GDPR Compliance Checklist

If you have EU users, ensure:

- [ ] Cookie consent banner (if using non-essential cookies)
- [ ] Right to access data (provide export feature)
- [ ] Right to deletion (account deletion feature)
- [ ] Right to portability (data export)
- [ ] Clear consent for data processing
- [ ] Data Processing Agreement with OpenAI (if required)

## ⚠️ TODO: Replace Placeholders

Before going live, update these in the documents:

1. ✅ **Email address**: Updated to linkedinleadchecker@gmail.com
2. ✅ **Jurisdiction**: Set to Spanish law
3. **Company name**: If you have a registered company, add it
4. **Website URL**: Replace example URLs with your actual domain

## 📝 Recommended: Create HTML Versions

Convert the markdown to HTML for your website:

```bash
# Example using pandoc (or do it manually)
pandoc PRIVACY_POLICY.md -o web/privacy-policy.html --standalone
pandoc TERMS_OF_SERVICE.md -o web/terms-of-service.html --standalone
```

Or create simple HTML pages with your website's styling.

## 🎨 Styling Recommendations

Make legal pages user-friendly:

```css
.legal-document {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
  font-size: 16px;
  line-height: 1.6;
}

.legal-document h1 {
  font-size: 32px;
  margin-bottom: 10px;
}

.legal-document h2 {
  font-size: 24px;
  margin-top: 30px;
  color: #333;
}

.legal-document ul {
  list-style: none;
  padding-left: 20px;
}

.legal-document ul li::before {
  content: "✅ ";
  margin-right: 8px;
}
```

## 🚀 Quick Start

1. Review and customize the documents (especially contact info)
2. Convert to HTML and add to your website
3. Add footer links to landing page
4. Add links to Chrome extension popup
5. Update manifest.json with privacy policy URL
6. Add terms acceptance checkbox to sign-up flow
7. Test all links before deploying

## 📞 Legal Disclaimer

These documents are templates and starting points. While they cover common scenarios, you should:

- Have a lawyer review them if handling sensitive data
- Ensure compliance with your local laws
- Update them as your service evolves
- Keep the "Last Updated" date current

---

**Questions?** These are solid starting points for a SaaS + Chrome Extension. Customize them to match your specific needs and jurisdiction.
