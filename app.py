
from flask import Flask, request, jsonify, render_template
import threading

from image_processing import image_processing
from store_db import fetch_all_images, create_or_reset_users_table

create_or_reset_users_table()
app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/upload_image', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    file.save(file.filename)
    file.seek(0)

    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        threading.Thread(target=image_processing, args=(file,)).start()
        return jsonify({'message': 'File uploaded successfully!'}), 200

    return jsonify({'message': 'Invalid file type'}), 400

@app.route('/fetch_images', methods=['GET'])
def fetch_images():
    images = fetch_all_images()
    images_list = [{'id': image[0], 'image_path': image[1], 'description': image[2]} for image in images]
    return jsonify(images_list), 200


@app.route('/')
def index():
    return render_template('UI.html')

if __name__ == '__main__':
    app.run(port=8080, debug=True)
