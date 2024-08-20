from flask import Flask
from routes.convert import convert_bp
from routes.transcribe import transcribe_bp
from routes.combine import combine_bp
from routes.audio_mixing import audio_mixing_bp
from routes.gdrive_upload import gdrive_upload_bp
from routes.authentication import auth_bp  # Import the auth_bp blueprint

app = Flask(__name__)

# Register blueprints
app.register_blueprint(convert_bp)
app.register_blueprint(transcribe_bp)
app.register_blueprint(combine_bp)
app.register_blueprint(audio_mixing_bp)
app.register_blueprint(gdrive_upload_bp)
app.register_blueprint(auth_bp)  # Register the auth_bp blueprint

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
