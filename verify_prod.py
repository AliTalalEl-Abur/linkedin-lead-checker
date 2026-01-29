#!/usr/bin/env python
"""Production verification script (Render + Vercel + Stripe).

Requires env vars:
    PROD_BACKEND_URL
    PROD_FRONTEND_URL
    TEST_EMAIL
    TEST_PASSWORD
Optional:
    PAID_TEST_USER=true
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"ERROR: Missing required env var: {name}")
        sys.exit(1)
    if "localhost" in value or "127.0.0.1" in value:
        print(f"ERROR: {name} must not use localhost or 127.0.0.1")
        sys.exit(1)
    return value


def http_request(url: str, method: str = "GET", data: dict | None = None, headers: dict | None = None):
    payload = None
    req_headers = headers or {}
    if data is not None:
        payload = json.dumps(data).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=payload, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read()
            return resp.status, body
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read() or b""


def check_status(label: str, condition: bool, details: str = "") -> bool:
    if condition:
        print(f"✅ {label}")
        return True
    print(f"❌ {label}")
    if details:
        print(details)
    return False


def main():
    backend_url = require_env("PROD_BACKEND_URL").rstrip("/")
    frontend_url = require_env("PROD_FRONTEND_URL").rstrip("/")
    test_email = require_env("TEST_EMAIL")
    test_password = require_env("TEST_PASSWORD")
    paid_test_user = os.environ.get("PAID_TEST_USER", "").strip().lower() == "true"

    print("\n== Production Verification ==")
    failures = 0

    # 1) GET /health
    try:
        status, body = http_request(f"{backend_url}/health")
        ok = check_status("1) GET /health", status == 200, body.decode("utf-8", errors="ignore"))
        failures += 0 if ok else 1
    except Exception as exc:
        ok = check_status("1) GET /health", False, str(exc))
        failures += 1

    # 2) Signup/login -> token
    token = ""
    try:
        status, body = http_request(
            f"{backend_url}/auth/login",
            method="POST",
            data={"email": test_email, "password": test_password},
        )
        data = json.loads(body.decode("utf-8", errors="ignore") or "{}")
        token = data.get("access_token", "")
        ok = check_status("2) POST /auth/login -> token", status == 200 and bool(token), body.decode("utf-8", errors="ignore"))
        failures += 0 if ok else 1
    except Exception as exc:
        ok = check_status("2) POST /auth/login -> token", False, str(exc))
        failures += 1

    # 3) GET /billing/status (free)
    billing_status = None
    if token:
        try:
            status, body = http_request(
                f"{backend_url}/billing/status",
                headers={"Authorization": f"Bearer {token}"}
            )
            billing_status = json.loads(body.decode("utf-8", errors="ignore") or "{}")
            plan = billing_status.get("plan")
            is_free = plan == "free"
            ok = check_status(
                "3) GET /billing/status (free)",
                status == 200 and (is_free if not paid_test_user else True),
                body.decode("utf-8", errors="ignore")
            )
            failures += 0 if ok else 1
        except Exception as exc:
            ok = check_status("3) GET /billing/status (free)", False, str(exc))
            failures += 1
    else:
        ok = check_status("3) GET /billing/status (free)", False, "Missing token")
        failures += 1

    # 4) POST /analyze preview (OK)
    if token:
        try:
            payload = {
                "profileUrl": f"{frontend_url}/profile/test",
                "profileExtract": {
                    "name": "Test User",
                    "headline": "Test Lead",
                    "experience": ["Test Role"]
                },
                "mode": "preview"
            }
            status, body = http_request(
                f"{backend_url}/analyze",
                method="POST",
                headers={"Authorization": f"Bearer {token}"},
                data=payload,
            )
            data = json.loads(body.decode("utf-8", errors="ignore") or "{}")
            ok = check_status(
                "4) POST /analyze preview",
                status == 200 and data.get("mode") == "preview",
                body.decode("utf-8", errors="ignore")
            )
            failures += 0 if ok else 1
        except Exception as exc:
            ok = check_status("4) POST /analyze preview", False, str(exc))
            failures += 1
    else:
        ok = check_status("4) POST /analyze preview", False, "Missing token")
        failures += 1

    # 5) POST /billing/checkout plan=starter (Stripe URL)
    if token:
        try:
            return_url = f"{frontend_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}"
            status, body = http_request(
                f"{backend_url}/billing/checkout",
                method="POST",
                headers={"Authorization": f"Bearer {token}"},
                data={"plan": "starter", "return_url": return_url},
            )
            data = json.loads(body.decode("utf-8", errors="ignore") or "{}")
            url = data.get("url", "")
            ok = check_status(
                "5) POST /billing/checkout plan=starter -> Stripe URL",
                status == 200 and "stripe.com" in url,
                body.decode("utf-8", errors="ignore")
            )
            failures += 0 if ok else 1
        except Exception as exc:
            ok = check_status("5) POST /billing/checkout plan=starter -> Stripe URL", False, str(exc))
            failures += 1
    else:
        ok = check_status("5) POST /billing/checkout plan=starter -> Stripe URL", False, "Missing token")
        failures += 1

    # 6) Optional paid test: POST /analyze ai and verify decrement
    if paid_test_user and token:
        try:
            status, body = http_request(
                f"{backend_url}/billing/status",
                headers={"Authorization": f"Bearer {token}"}
            )
            before = json.loads(body.decode("utf-8", errors="ignore") or "{}")
            before_remaining = max(0, (before.get("usage_limit", 0) - before.get("usage_current", 0)))

            payload = {
                "profileUrl": f"{frontend_url}/profile/test-ai",
                "profileExtract": {
                    "name": "Paid Test",
                    "headline": "AI Test",
                    "experience": ["AI Role"]
                },
                "mode": "ai"
            }
            status, body = http_request(
                f"{backend_url}/analyze",
                method="POST",
                headers={"Authorization": f"Bearer {token}"},
                data=payload,
            )
            data = json.loads(body.decode("utf-8", errors="ignore") or "{}")
            after_remaining = data.get("remaining")
            ok = check_status(
                "6) POST /analyze ai (decrement remaining)",
                status == 200 and isinstance(after_remaining, int) and after_remaining == max(0, before_remaining - 1),
                body.decode("utf-8", errors="ignore")
            )
            failures += 0 if ok else 1
        except Exception as exc:
            ok = check_status("6) POST /analyze ai (decrement remaining)", False, str(exc))
            failures += 1

    print("\n✅ Production checks passed" if failures == 0 else "\n❌ Production checks failed")
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()
