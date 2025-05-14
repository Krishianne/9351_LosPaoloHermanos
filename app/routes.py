from flask import Blueprint, render_template, request, Flask, jsonify
import joblib
import os
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from PIL import Image
import numpy as np
import io
import base64
import cv2

# Create a Blueprint for organizing routes
main = Blueprint('main', __name__)

# Load the YOLO model
model = None

def load_model():
    global model
    try:
        model_path = os.path.join(os.path.dirname(__file__), 'model', 'yolo_model.pt')
        model = YOLO(model_path)
        print("The model was loaded successfully!")
        return True
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

# Try to load the model when the app starts
load_model()

# Function to segment coffee beans from the image
def segment_coffee_beans(image_path):
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        raise Exception(f"Could not read image at {image_path}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply threshold to separate beans from white background
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Apply morphological operations to remove noise
    kernel = np.ones((5,5), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    
    # Find contours of beans
    contours, _ = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by area to remove small noise
    min_area = 100  # Adjust based on your image size and bean size
    bean_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
    
    # Create individual bean images
    bean_images = []
    bean_boxes = []
    padding = 10  # Add some padding around each bean
    
    for i, cnt in enumerate(bean_contours):
        # Get bounding box
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Add padding but stay within image bounds
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(img.shape[1], x + w + padding)
        y2 = min(img.shape[0], y + h + padding)
        
        # Crop the bean
        bean_img = img[y1:y2, x1:x2]
        
        # Only add if the bean image is not empty
        if bean_img.size > 0:
            bean_images.append(bean_img)
            bean_boxes.append((x1, y1, x2, y2))
    
    return img, bean_images, bean_boxes

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

        img, bean_images, _ = segment_coffee_beans(file_path)
        grades = []
        for i, bean_img in enumerate(bean_images):
            bean_filename = f"bean_{i}.jpg"
            bean_path = os.path.join(upload_folder, bean_filename)
            cv2.imwrite(bean_path, bean_img)
            results = model(bean_path)

            result = results[0]

            if result.boxes and result.boxes.cls.numel() > 0:
                class_id = int(result.boxes.cls[0].item())
                class_name = model.names[class_id]
                grades.append(class_name)            

        grade_order = ['C', 'BULK', 'BITS', 'PB-II', 'PB-I', 'AB', 'A', 'AA', 'AAA']
        highest_grade = sorted(grades, key=lambda x: grade_order.index(x))[-1] if grades else "No beans detected"


        return jsonify({
            'message': 'File uploaded and classified',
            'filename': filename,
            'url': f'/static/uploads/{filename}',
            'highest_grade': highest_grade
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


@main.route('/predict', methods=['POST'])
def predict():
    if model is None:
        success = load_model()
        if not success:
            return jsonify({'error': 'Model not available'}), 500

    data = request.get_json()
    image_path = data.get('image_path')
    
    if not image_path:
        return jsonify({'error': 'No image provided'}), 400
    
    # Convert relative path to absolute
    full_path = os.path.join(os.getcwd(), 'app', image_path.lstrip('/'))
    
    try:
        results = model(full_path)
        result = results[0]
        predictions = []
        class_names = model.names
        for box in result.boxes:
            class_id = int(box.cls[0].item())
            predictions.append({
                'class': class_names[class_id],
                'confidence': float(box.conf[0].item()),
                'bbox': box.xyxy[0].tolist()
            })
        annotated_img = result.plot()
        img_pil = Image.fromarray(annotated_img)
        buffered = io.BytesIO()
        img_pil.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return jsonify({
            'success': True,
            'predictions': predictions,
            'annotated_image': f'data:image/jpeg;base64,{img_str}'
        }), 200
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500