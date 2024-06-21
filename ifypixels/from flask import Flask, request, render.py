from flask import Flask, request, render_template, send_from_directory
from PIL import Image
import rembg
import uuid
import os
import logging

# Existing upload folder configuration (unchanged)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads/remove')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Configure logging (optional)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMPLATE_FOLDER'] = 'templates'  # Assuming templates folder

def remove_background(image_path):
    try:
        input_image = Image.open(image_path)
        output_image = rembg.remove(input_image)

        # Ensure format is retrieved before potential conversion
        image_format = output_image.format.lower()  # Get format first

        # Convert to RGB only if necessary (avoid unnecessary conversion)
        if image_format != 'rgb':
            output_image = output_image.convert('RGB')  # Fix for JPEG format

        # Generate unique filename with extension
        unique_filename = f"{uuid.uuid4()}.{image_format}"
        output_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        output_image.save(output_path)
        return output_path
    except Exception as e:
        logging.error(f"Error removing background: {e.__class__}, {e}")  # Log detailed error
        return None  # Return None on error

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files['image']
        if uploaded_file.filename != '':
            # Validate allowed file types (optional)
            allowed_extensions = {'png', 'jpg', 'jpeg'}
            if uploaded_file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                return "Unsupported file format. Please upload PNG, JPG, or JPEG image."

            # Save uploaded image with unique filename
            image_path = remove_background(uploaded_file.stream)  # Use stream for large files
            if image_path:
                return render_template('result.html', output_path=image_path)
            else:
                # Check logged error for clues
                return "Error removing background! Check logs for details."
        else:
            return "No file selected!"

    return render_template('upload.html')  # Redirect to upload form on GET

@app.route('/uploads/remove/<filename>', methods=['POST'])  # Corrected route (optional POST method)
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
