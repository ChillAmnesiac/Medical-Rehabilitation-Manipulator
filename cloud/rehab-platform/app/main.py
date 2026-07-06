from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import inspect, text

from app.api.routes import auth, rehab_app
from app.core.config import Settings
from app.db import Base, make_sessionmaker
from app.services.auth import seed_default_user


def create_app(database_url: str | None = None) -> FastAPI:
    settings = Settings()
    if database_url is not None:
        settings.database_url = database_url

    app = FastAPI(title=settings.app_name)
    app.state.settings = settings
    app.state.session_factory = make_sessionmaker(settings.database_url)

    engine = app.state.session_factory.kw["bind"]
    Base.metadata.create_all(engine)
    ensure_runtime_schema(engine)
    with app.state.session_factory() as session:
        seed_default_user(session)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request, exc: HTTPException):
        detail = exc.detail if isinstance(exc.detail, dict) else {}
        code = detail.get("code", "HTTP_ERROR")
        message = detail.get("message", str(exc.detail))
        error = {"code": code, "message": message}
        for key, value in detail.items():
            if key not in error:
                error[key] = value
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": error},
        )

    @app.get("/health")
    def health():
        return {"data": {"status": "ok", "service": "rehab-platform"}}

    app.include_router(auth.router)
    app.include_router(rehab_app.router)
    return app


def ensure_runtime_schema(engine) -> None:
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "phone_verified_at" not in user_columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE users ADD COLUMN phone_verified_at DATETIME"))


app = create_app()
