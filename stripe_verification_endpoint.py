"""
Stripe Verification API Endpoint (Optional)

Add this to your FastAPI backend to expose verification as an endpoint.

Usage:
    1. Copy this code to app/api/routes/admin.py (or create new file)
    2. Register router in app/main.py
    3. Protect with authentication/authorization
    4. Access at: GET /admin/verify-stripe
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import stripe
from datetime import datetime

# Initialize router
router = APIRouter(prefix="/admin", tags=["admin"])

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Expected configuration
EXPECTED_PLANS = {
    'starter': {
        'name': 'LinkedIn Lead Checker – Starter',
        'price_env': 'STRIPE_PRICE_STARTER_ID',
        'expected_price': 9.00,
        'analyses': 40
    },
    'pro': {
        'name': 'LinkedIn Lead Checker – Pro',
        'price_env': 'STRIPE_PRICE_PRO_ID',
        'expected_price': 19.00,
        'analyses': 150
    },
    'team': {
        'name': 'LinkedIn Lead Checker – Team',
        'price_env': 'STRIPE_PRICE_TEAM_ID',
        'expected_price': 49.00,
        'analyses': 500
    }
}


# Response models
class VerificationError(BaseModel):
    message: str
    severity: str  # "error" or "warning"


class PlanStatus(BaseModel):
    plan_key: str
    product_name: str
    price_id: str
    expected_price: float
    actual_price: Optional[float]
    status: str  # "ok", "error", "warning"
    message: Optional[str]


class StripeVerificationResponse(BaseModel):
    success: bool
    timestamp: str
    active_products: int
    expected_products: int
    errors: List[VerificationError]
    warnings: List[VerificationError]
    plan_statuses: List[PlanStatus]
    summary: Dict[str, any]


# Dependency for admin authentication (customize as needed)
async def verify_admin_access():
    """
    Add your authentication/authorization logic here.
    
    Examples:
    - Check JWT token for admin role
    - Verify API key
    - Check IP whitelist
    - etc.
    """
    # TODO: Implement authentication
    # For now, this is wide open - SECURE THIS BEFORE PRODUCTION!
    pass
    
    # Example implementation:
    # from app.core.auth import get_current_user
    # user = await get_current_user(token)
    # if not user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")


@router.get("/verify-stripe", response_model=StripeVerificationResponse)
async def verify_stripe_sync(admin: None = Depends(verify_admin_access)):
    """
    Verify Stripe synchronization.
    
    Checks:
    - Exactly 3 active products
    - Correct product names
    - Prices match expected values
    - No duplicates
    - Backend price_ids are active
    - Backend/Stripe synchronization
    
    Returns:
        VerificationResponse with success status, errors, warnings, and detailed info
    """
    errors = []
    warnings = []
    plan_statuses = []
    
    try:
        # Load backend configuration
        backend_config = {}
        for plan_key, plan_info in EXPECTED_PLANS.items():
            price_id = os.getenv(plan_info['price_env'])
            if price_id:
                backend_config[plan_key] = {
                    'price_id': price_id,
                    'expected_name': plan_info['name'],
                    'expected_price': plan_info['expected_price'],
                    'analyses': plan_info['analyses']
                }
            else:
                errors.append(VerificationError(
                    message=f"Missing environment variable: {plan_info['price_env']}",
                    severity="error"
                ))
        
        # Load Stripe data
        products = stripe.Product.list(limit=100)
        active_products = [p for p in products.data if p.active]
        
        # Check product count
        if len(active_products) != 3:
            errors.append(VerificationError(
                message=f"Expected 3 active products, found {len(active_products)}",
                severity="error"
            ))
        
        # Check each plan
        for plan_key, config in backend_config.items():
            plan_status = PlanStatus(
                plan_key=plan_key,
                product_name=config['expected_name'],
                price_id=config['price_id'],
                expected_price=config['expected_price'],
                actual_price=None,
                status="ok",
                message=None
            )
            
            # Find matching product
            matching_products = [
                p for p in active_products 
                if p.name == config['expected_name']
            ]
            
            if not matching_products:
                plan_status.status = "error"
                plan_status.message = f"Product not found in Stripe"
                errors.append(VerificationError(
                    message=f"{plan_key}: Product '{config['expected_name']}' not found",
                    severity="error"
                ))
            elif len(matching_products) > 1:
                plan_status.status = "error"
                plan_status.message = f"Multiple products found ({len(matching_products)})"
                errors.append(VerificationError(
                    message=f"{plan_key}: Multiple products with same name",
                    severity="error"
                ))
            else:
                product = matching_products[0]
                
                # Check prices
                prices = stripe.Price.list(product=product.id, limit=100)
                active_prices = [p for p in prices.data if p.active]
                
                if not active_prices:
                    plan_status.status = "error"
                    plan_status.message = "No active prices"
                    errors.append(VerificationError(
                        message=f"{plan_key}: No active prices found",
                        severity="error"
                    ))
                else:
                    # Check if backend price_id matches
                    backend_price_id = config['price_id']
                    matching_price = None
                    
                    for price in active_prices:
                        if price.id == backend_price_id:
                            matching_price = price
                            break
                    
                    if matching_price:
                        actual_price = matching_price.unit_amount / 100
                        plan_status.actual_price = actual_price
                        
                        if actual_price == config['expected_price']:
                            plan_status.status = "ok"
                            plan_status.message = "All checks passed"
                        else:
                            plan_status.status = "error"
                            plan_status.message = f"Price mismatch: expected ${config['expected_price']}, got ${actual_price}"
                            errors.append(VerificationError(
                                message=f"{plan_key}: Price mismatch",
                                severity="error"
                            ))
                    else:
                        plan_status.status = "error"
                        plan_status.message = "Backend price_id not found in Stripe"
                        errors.append(VerificationError(
                            message=f"{plan_key}: Backend price_id doesn't match Stripe",
                            severity="error"
                        ))
                    
                    # Check for multiple active prices (warning)
                    if len(active_prices) > 1:
                        warnings.append(VerificationError(
                            message=f"{plan_key}: Multiple active prices ({len(active_prices)})",
                            severity="warning"
                        ))
            
            plan_statuses.append(plan_status)
        
        # Check for duplicates
        names = [p.name for p in active_products]
        duplicate_names = [name for name in names if names.count(name) > 1]
        if duplicate_names:
            for dup_name in set(duplicate_names):
                errors.append(VerificationError(
                    message=f"Duplicate product: {dup_name}",
                    severity="error"
                ))
        
        # Build response
        success = len(errors) == 0
        
        return StripeVerificationResponse(
            success=success,
            timestamp=datetime.utcnow().isoformat(),
            active_products=len(active_products),
            expected_products=3,
            errors=errors,
            warnings=warnings,
            plan_statuses=plan_statuses,
            summary={
                "total_errors": len(errors),
                "total_warnings": len(warnings),
                "plans_ok": sum(1 for ps in plan_statuses if ps.status == "ok"),
                "plans_error": sum(1 for ps in plan_statuses if ps.status == "error"),
                "ready_for_production": success
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Verification failed: {str(e)}"
        )


@router.get("/stripe-health", response_model=Dict[str, any])
async def stripe_health_check(admin: None = Depends(verify_admin_access)):
    """
    Quick health check for Stripe configuration.
    
    Returns:
        Simple OK/ERROR status with basic metrics
    """
    try:
        # Quick checks
        products = stripe.Product.list(limit=100)
        active_products = [p for p in products.data if p.active]
        
        # Load backend config
        backend_config = {}
        for plan_key, plan_info in EXPECTED_PLANS.items():
            price_id = os.getenv(plan_info['price_env'])
            if price_id:
                backend_config[plan_key] = price_id
        
        # Simple status
        status = "OK" if len(active_products) == 3 and len(backend_config) == 3 else "ERROR"
        
        return {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "active_products": len(active_products),
            "configured_plans": len(backend_config),
            "expected": {
                "products": 3,
                "plans": 3
            },
            "healthy": status == "OK"
        }
        
    except Exception as e:
        return {
            "status": "ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "healthy": False
        }


# Example usage in app/main.py:
"""
from app.api.routes.stripe_verification_endpoint import router as verification_router

app.include_router(verification_router)
"""

# Example curl commands:
"""
# Full verification
curl BACKEND_URL/admin/verify-stripe

# Quick health check
curl BACKEND_URL/admin/stripe-health

# With authentication (example)
curl -H "Authorization: Bearer YOUR_TOKEN" BACKEND_URL/admin/verify-stripe
"""
