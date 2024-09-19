from .combine_videos import combine_bp
from .gdrive_upload import gdrive_upload_bp
from .media_to_mp3 import convert_bp
from .caption_video import caption_bp  # Add this line

def register_blueprints(app):
    app.register_blueprint(combine_bp)
    app.register_blueprint(gdrive_upload_bp)
    app.register_blueprint(convert_bp)
    app.register_blueprint(caption_bp)  # Add this line