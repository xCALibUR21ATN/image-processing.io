from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

@app.route('/process-images', methods=['POST'])
def process_images():
    if 'image1' not in request.files or 'image2' not in request.files:
        return jsonify({"error": "Both image1 and image2 must be uploaded"}), 400

    image1 = request.files['image1']
    image2 = request.files['image2']

    filename1 = secure_filename(image1.filename)
    filename2 = secure_filename(image2.filename)

    # Here you can add your image processing code with cv2, skimage, etc.

    # For now, just return the filenames as a demonstration
    return jsonify({
        "image1_name": filename1,
        "image2_name": filename2,
        "message": "Images received and processed"
    })

if __name__ == '__main__':
    app.run(debug=True)
