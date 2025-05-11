from flask import Blueprint, render_template, request, Flask, jsonify
import joblib
import os
from werkzeug.utils import secure_filename

# Create a Blueprint for organizing routes
main = Blueprint('main', __name__)

# # Load the model once when the app starts
# model_path = os.path.join(os.path.dirname(__file__), 'model', 'model.pkl')
# model = joblib.load(model_path)

@main.route('/')
def index():
    return render_template('homepage.html')  # Input form

@main.route('/about')
def about():
    return render_template('about.html')  # About page


@main.route('/class')
def classifier():
    return render_template('classifier.html') # Navigate to classifier

@main.route('/upload', methods=['POST'])
def upload():
    if 'imageInput' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['imageInput']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)  # Ensure folder exists
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        return jsonify({
            'message': 'File uploaded',
            'filename': filename,  # for deletion
            'url': f'/static/uploads/{filename}'  # for preview
        }), 200

    return jsonify({'error': 'Upload failed'}), 400

@main.route('/delete-image', methods=['POST'])
def delete_image():
    data = request.get_json()
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'Filename not provided'}), 400

    file_path = os.path.join(os.getcwd(), 'app', 'static', 'uploads', filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'message': 'File deleted'}), 200

    return jsonify({'error': 'File not found'}), 404


# @main.route('/predict', methods=['POST'])
# def predict():
#     if request.method == 'POST':
#         # Extract features from form (example: 3 inputs)
#         f1 = float(request.form['feature1'])
#         f2 = float(request.form['feature2'])
#         f3 = float(request.form['feature3'])

#         # Make prediction
#         prediction = model.predict([[f1, f2, f3]])
#         grade = prediction[0]

#         return render_template('result.html', prediction=grade)
