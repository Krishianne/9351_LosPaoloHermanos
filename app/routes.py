from flask import Blueprint, render_template, request, Flask
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
        return {'error': 'No file part'}, 400

    file = request.files['imageInput']
    if file.filename == '':
        return {'error': 'No selected file'}, 400

    # Check and save file
    if file:
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(os.getcwd(), 'app','static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)  # Ensure folder exists
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        return {'message': 'File uploaded', 'url': f'/static/uploads/{filename}'}, 200

    return {'error': 'Upload failed'}, 400


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
