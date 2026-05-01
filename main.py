import logging
logging.basicConfig(level=logging.DEBUG)

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from datetime import timedelta
import os

load_dotenv()

app = Flask(__name__)
app.url_map.strict_slashes = False

# ── FIX 1: Render gives postgres://, SQLAlchemy needs postgresql:// ──
db_url = os.getenv("DATABASE_URL", "")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "fallback-secret")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)

from app.models import db
db.init_app(app)
JWTManager(app)

# ── FIX 2: Register blueprints FIRST, then apply CORS ──
with app.app_context():
    from app.models.user import User
    from app.models.log import Log
    from app.models.alert import Alert
    from app.models.metric import Metric
    from app.routes.auth import bp as auth_bp
    from app.routes.logs import bp as logs_bp
    from app.routes.alerts import bp as alerts_bp
    from app.routes.metrics import bp as metrics_bp
    from app.routes.users import bp as users_bp

    app.register_blueprint(auth_bp,    url_prefix="/api/auth")
    app.register_blueprint(logs_bp,    url_prefix="/api/logs")
    app.register_blueprint(alerts_bp,  url_prefix="/api/alerts")
    app.register_blueprint(metrics_bp, url_prefix="/api/metrics")
    app.register_blueprint(users_bp,   url_prefix="/api/users")

    db.create_all()
    print("✅ Database tables created successfully.")

# ── CORS applied AFTER all routes are registered ──
CORS(app, origins=[
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://clever-liger-edbbea.netlify.app"
], supports_credentials=True)

if __name__ == "__main__":
    app.run(debug=True)