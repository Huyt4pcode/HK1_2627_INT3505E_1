from flask import Blueprint, jsonify
from sqlalchemy import text
from ..extensions import db

health_bp = Blueprint("health", __name__, url_prefix="")

@health_bp.get("/healthz")
def liveness():
    return jsonify({"status": "ok"}), 200


@health_bp.get("/ready")
def readiness():
    checks = {}
    try:
        db.session.execute(text("SELECT 1"))
        checks["db"] = "ok"
    except Exception:
        checks["db"] = "err"

    ok = all(v == "ok" for v in checks.values())
    status_code = 200 if ok else 503
    
    return jsonify({
        "status": "ok" if ok else "degraded",
        "checks": checks
    }), status_code