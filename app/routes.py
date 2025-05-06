from flask import Blueprint, render_template, request
import joblib
import os

# Create a Blueprint for organizing routes
main = Blueprint('main', __name__)

# # Load the model once when the app starts
# model_path = os.path.join(os.path.dirname(__file__), 'model', 'model.pkl')
# model = joblib.load(model_path)

@main.route('/')
def index():
    return render_template('classifier.html')  # Input form

@main.route('/about')
def about():
    return render_template('about.html')  # About page


@main.route('/class')
def classifier():
    return render_template('classifier.html') # Navigate to classifier

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
