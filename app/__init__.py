import os

from flask import Flask, render_template

from app.extensions import csrf, db, login_manager
from app.logging_config import setup_logging


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")
        if config_name not in ("development", "production", "testing"):
            config_name = "development"

    from config import config_by_name

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    setup_logging(app)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    from app.routes.api import api_bp
    from app.routes.auth import auth_bp
    from app.routes.events import events_bp
    from app.routes.main import main_bp
    from app.routes.profile import profile_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(api_bp)

    # The JSON API is stateless and token-authenticated, not cookie/session
    # based, so CSRF protection does not apply to it.
    csrf.exempt(api_bp)

    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    @app.context_processor
    def inject_globals():
        from datetime import datetime

        from app.models import CATEGORIES, CATEGORY_LABELS

        return {
            "categories": CATEGORIES,
            "category_labels": CATEGORY_LABELS,
            "current_year": datetime.utcnow().year,
        }

    register_template_filters(app)

    return app


KA_MONTHS = [
    "", "იანვარი", "თებერვალი", "მარტი", "აპრილი", "მაისი", "ივნისი",
    "ივლისი", "აგვისტო", "სექტემბერი", "ოქტომბერი", "ნოემბერი", "დეკემბერი",
]
KA_MONTHS_SHORT = [
    "", "იან", "თებ", "მარ", "აპრ", "მაი", "ივნ",
    "ივლ", "აგვ", "სექ", "ოქტ", "ნოე", "დეკ",
]


def register_template_filters(app):
    @app.template_filter("kadate")
    def kadate(value, style="full"):
        """Format a datetime in Georgian (month names spelled out, not locale-dependent)."""
        if value is None:
            return ""
        if style == "full":
            return f"{value.day} {KA_MONTHS[value.month]} {value.year}, {value:%H:%M}"
        if style == "date":
            return f"{value.day} {KA_MONTHS[value.month]} {value.year}"
        if style == "monthyear":
            return f"{KA_MONTHS[value.month]} {value.year}"
        if style == "day":
            return f"{value.day:02d}"
        if style == "mon":
            return KA_MONTHS_SHORT[value.month]
        if style == "time":
            return f"{value:%H:%M}"
        return str(value)


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error("Internal server error: %s", error)
        return render_template("errors/500.html"), 500
