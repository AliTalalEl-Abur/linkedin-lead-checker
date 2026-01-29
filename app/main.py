import logging
from uuid import uuid4

from fastapi import FastAPI
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analyze import router as analyze_router
from app.api.routes.auth import router as auth_router
from app.api.routes.billing import router as billing_router
from app.api.routes.events import router as events_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.health import router as health_router
from app.api.routes.user import router as user_router
from app.core.config import get_settings
from app.core.db import Base, get_engine

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    logger.info("="*60)
    logger.info("Starting LinkedIn Lead Checker API")
    logger.info("="*60)
    logger.info("Environment: %s", settings.env)
    
    # Validate required environment variables
    _validate_required_env(settings)
    
    # Log optional service status
    _log_service_status(settings)
    
    app = FastAPI(title="LinkedIn Lead Checker API", version="1.0.0")

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,  # type: ignore[arg-type]
        allow_origin_regex=settings.cors_allow_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(analyze_router)
    app.include_router(billing_router)
    app.include_router(events_router)
    app.include_router(feedback_router)

    # Ensure all models are imported before creating tables
    from app import models as _models  # noqa: F401

    # Initialize database tables
    Base.metadata.create_all(bind=get_engine())
    logger.info("Database tables initialized")
    
    # Log kill switch status
    if settings.disable_all_analyses:
        logger.warning("KILL SWITCH ACTIVE: All analyses disabled")
    if settings.disable_free_plan:
        logger.warning("KILL SWITCH ACTIVE: Free plan disabled")
    
    logger.info("="*60)
    logger.info("Backend ready to receive traffic")
    logger.info("="*60)

    return app


def _validate_required_env(settings: object) -> None:
    """Validate required environment variables at startup."""
    errors = []
    
    # DATABASE_URL is required
    database_url = getattr(settings, 'database_url', None)
    if not database_url:
        errors.append("DATABASE_URL is required")
    
    # JWT_SECRET_KEY must be strong (32+ chars)
    jwt_secret_key = getattr(settings, 'jwt_secret_key', None)
    if not jwt_secret_key:
        errors.append("JWT_SECRET_KEY is required")
    elif len(jwt_secret_key) < 32:
        errors.append("JWT_SECRET_KEY must be at least 32 characters")
    elif jwt_secret_key == "dev-secret-key-change-in-production-at-least-32-chars-long":
        env = getattr(settings, 'env', 'dev')
        if env == "prod":
            errors.append("JWT_SECRET_KEY must be changed in production")
    
    if errors:
        for error in errors:
            logger.error("STARTUP VALIDATION ERROR: %s", error)
        raise RuntimeError(f"Missing required environment variables: {', '.join(errors)}")
    
    logger.info("✓ Required environment variables validated")


def _log_service_status(settings: object) -> None:
    """Log status of optional services at startup."""
    # OpenAI status
    openai_enabled = getattr(settings, 'openai_enabled', False)
    has_openai_key = bool(getattr(settings, 'openai_api_key', None))
    
    if not openai_enabled:
        logger.info("openai_enabled=false")
    elif not has_openai_key:
        logger.info("OpenAI: MOCK MODE (no API key - preview only, zero cost)")
    else:
        logger.info("openai_enabled=true")
    
    # Stripe status
    has_stripe_key = bool(getattr(settings, 'stripe_api_key', None))
    has_starter_price = bool(getattr(settings, 'stripe_price_starter_id', None))
    has_pro_price = bool(getattr(settings, 'stripe_price_pro_id', None))
    has_team_price = bool(getattr(settings, 'stripe_price_team_id', None))
    has_webhook_secret = bool(getattr(settings, 'stripe_webhook_secret', None))
    
    if has_stripe_key:
        logger.info("Stripe: ENABLED (billing available)")
        logger.info("  - starter_price_id: %s", "configured" if has_starter_price else "missing")
        logger.info("  - pro_price_id: %s", "configured" if has_pro_price else "missing")
        logger.info("  - team_price_id: %s", "configured" if has_team_price else "missing")
        logger.info("  - webhook_secret: %s", "configured" if has_webhook_secret else "missing")
        if not (has_starter_price or has_pro_price or has_team_price):
            logger.warning("WARNING: Stripe API key configured but no price IDs set. Checkout will fail.")
    else:
        logger.info("Stripe: DISABLED (no API key - billing unavailable)")
    
    # Render deployment detection
    is_render = bool(getattr(settings, 'render_deploy', False))
    if is_render:
        logger.info("render_deploy=true")
    
    # Final status
    logger.info("service_ready=true")


app = create_app()
