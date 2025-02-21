import os
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from utils.model import analyze_xray

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure upload settings
UPLOAD_FOLDER = '/tmp/uploads'
MODEL_FOLDER = 'model'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Ensure required directories exist
for folder in [UPLOAD_FOLDER, MODEL_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)
        logging.info(f"Created directory: {folder}")

# Log model file status
model_path = os.path.join(MODEL_FOLDER, 'osteoporosis_model.h5')
if os.path.exists(model_path):
    logging.info("Model file found at: %s", model_path)
else:
    logging.warning("Model file not found. Please place 'osteoporosis_model.h5' in the 'model' directory")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Analyze the X-ray
        result = analyze_xray(filepath)

        # Clean up the uploaded file
        os.remove(filepath)

        return jsonify(result)
    except Exception as e:
        logging.error(f"Error processing upload: {str(e)}")
        return jsonify({'error': 'Error processing upload'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File is too large'}), 413