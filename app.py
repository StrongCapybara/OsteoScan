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

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Check if model exists
    model_exists = os.path.exists(os.path.join(MODEL_FOLDER, 'osteoporosis_model.h5'))
    return render_template('index.html', model_ready=model_exists)

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

@app.route('/upload-model', methods=['POST'])
def upload_model():
    if 'model' not in request.files:
        return jsonify({'error': 'No model file provided'}), 400

    model_file = request.files['model']
    if model_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not model_file.filename.endswith('.h5'):
        return jsonify({'error': 'Invalid model file format. Please upload a .h5 file'}), 400

    try:
        filename = 'osteoporosis_model.h5'
        filepath = os.path.join(MODEL_FOLDER, filename)
        model_file.save(filepath)
        return jsonify({'success': 'Model uploaded successfully'})
    except Exception as e:
        logging.error(f"Error uploading model: {str(e)}")
        return jsonify({'error': 'Error uploading model'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File is too large'}), 413