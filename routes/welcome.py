from flask import Blueprint, jsonify

from version import BUILD_NUMBER

welcome_bp = Blueprint("welcome_bp", __name__)


@welcome_bp.route("/welcome", methods=["GET"])
def welcome():
    """
    Public entry route that reminds callers what the API is and includes the build number.
    """
    return (
        jsonify(
            {
                "message": "Welcome to the No-Code Architects Toolkit API.",
                "status": "ready",
                "build_number": BUILD_NUMBER,
            }
        ),
        200,
    )


@welcome_bp.route("/health", methods=["GET"])
def health():
    """
    Basic health check endpoint that can be used by uptime monitors.
    """
    return (
        jsonify(
            {
                "status": "healthy",
                "build_number": BUILD_NUMBER,
            }
        ),
        200,
    )
