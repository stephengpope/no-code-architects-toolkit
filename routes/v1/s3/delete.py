from flask import Blueprint, request, jsonify
from services.s3_toolkit import delete_from_s3
from config import get_s3_config

v1_s3_delete_bp = Blueprint("v1_s3_delete", __name__)

@v1_s3_delete_bp.route("/v1/s3/delete", methods=["POST"])
def s3_delete():
    try:
        data = request.get_json()
        file_key = data.get("file_key")
        if not file_key:
            return jsonify({"error": "file_key is required"}), 400

        # Берём настройки из .env через config.py
        s3_url, access_key, secret_key, bucket_name, region = get_s3_config()

        response = delete_from_s3(
            s3_url, access_key, secret_key, bucket_name, region, file_key
        )

        return jsonify({
            "status": "success",
            "file_key": file_key,
            "response": str(response)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
