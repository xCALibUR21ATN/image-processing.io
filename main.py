import os
import cv2
import time
import tempfile
import threading
from flask_cors import CORS
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_file
from generate import visualize_color_diff

app = Flask(__name__)
CORS(app)

tmp_dir = "tmp"
os.makedirs(tmp_dir, exist_ok=True)

def delayed_delete(path, delay=5):
    def delete_file():
        time.sleep(delay)
        try:
            os.remove(path)
            app.logger.info(f"Delayed deletion: removed {path}")
        except Exception as e:
            app.logger.error(f"Delayed deletion failed: {e}")
    threading.Thread(target=delete_file).start()

@app.route('/process-images', methods=['POST'])
def process_images():
    def resize_image(img, max_w=2000, max_h=2000):
        h, w = img.shape[:2]
        scale = min(max_w / w, max_h / h, 1)
        return cv2.resize(img, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA) if scale < 1 else img

    if 'image1' not in request.files or 'image2' not in request.files:
        return jsonify({'error': 'Please upload two images'}), 400

    img1_file = request.files['image1']
    img2_file = request.files['image2']
    fn1 = secure_filename(img1_file.filename)
    fn2 = secure_filename(img2_file.filename)
    p1 = os.path.join(tmp_dir, fn1); img1_file.save(p1)
    p2 = os.path.join(tmp_dir, fn2); img2_file.save(p2)

    img1 = resize_image(cv2.imread(p1), 1000, 1000)
    img2 = resize_image(cv2.imread(p2), 1000, 1000)

    # Cleanup input images
    for path in (p1, p2):
        try: os.remove(path)
        except: pass

    if img1 is None or img2 is None:
        return jsonify({'error': 'Invalid image files'}), 400

    result = visualize_color_diff(img1, img2, img1_n=fn1, img2_n=fn2)

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png', dir=tmp_dir)
    out_path = tmp_file.name
    tmp_file.close()
    cv2.imwrite(out_path, result)

    out_name = os.path.basename(out_path)
    download_url = f"{request.host_url}download/{out_name}"

    return jsonify({
        'message': f"Image uploaded: {fn1}\nImage uploaded: {fn2}\n\nSuccessfully Processed",
        'processedImageUrl': download_url,
        'fileName': out_name
    })

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(tmp_dir, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    response = send_file(
        file_path,
        as_attachment=True,
        download_name=filename
    )

    delayed_delete(file_path, delay=5)
    return response

if __name__ == '__main__':
    app.run(debug=True)
