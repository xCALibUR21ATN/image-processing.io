import os
import cv2
import base64
import numpy as np
import tempfile
from flask_cors import CORS
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_file, after_this_request
from generate import visualize_color_diff

app = Flask(__name__)
CORS(app)

tmp_dir = "tmp"
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

@app.route('/process-images', methods=['POST'])
def process_images():
    if 'image1' not in request.files or 'image2' not in request.files:
        return jsonify({'error': 'Please upload two images'}), 400

    img1_file = request.files['image1']
    img2_file = request.files['image2']

    filename1 = secure_filename(img1_file.filename)
    filename2 = secure_filename(img2_file.filename)
    
    img1_bytes = img1_file.read()
    img2_bytes = img2_file.read()

    nparr1 = np.frombuffer(img1_bytes, np.uint8)
    img1 = cv2.imdecode(nparr1, cv2.IMREAD_COLOR)

    nparr2 = np.frombuffer(img2_bytes, np.uint8)
    img2 = cv2.imdecode(nparr2, cv2.IMREAD_COLOR)

    # Add validation for decoded images
    if img1 is None or img2 is None:
        return jsonify({'error': 'Invalid image files'}), 400

    output_img = visualize_color_diff(img1, img2)

    # Use PNG format consistently
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png', dir=tmp_dir)
    output_path = tmp.name
    tmp.close()  # allow cv2 to write

    cv2.imwrite(output_path, output_img)

    if 'download' in request.args:
        @after_this_request
        def cleanup(response):
            try:
                os.remove(output_path)
            except Exception:
                pass
            return response

        return send_file(
            output_path,
            mimetype='image/png',
            as_attachment=True,
            download_name='result.png'
        )

    with open(output_path, 'rb') as f:
        output_bytes = f.read()

    os.remove(output_path)

    encoded_img = base64.b64encode(output_bytes).decode('utf-8')

    return jsonify({'image': encoded_img})


if __name__ == '__main__':
    app.run(debug=True)
