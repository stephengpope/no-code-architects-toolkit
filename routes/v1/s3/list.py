from flask import Blueprint, jsonify, request
from services.s3_toolkit import list_files
import os
from services.authentication import authenticate   # ⚡️ защита по API-ключу

s3_list_bp = Blueprint("s3_list", __name__)

@s3_list_bp.route("/v1/s3/list", methods=["GET"])
@authenticate
def list_s3_files():
    prefix = request.args.get("prefix", "")   # можно указать ?prefix=videos/
    files = list_files(
        os.getenv("S3_ENDPOINT_URL"),
        os.getenv("S3_ACCESS_KEY"),
        os.getenv("S3_SECRET_KEY"),
        os.getenv("S3_BUCKET_NAME"),
        os.getenv("S3_REGION", "us-east-1"),
        prefix=prefix
    )
    return jsonify({"files": files})
