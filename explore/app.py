from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
from PIL import Image
import tensorflow as tf
import io
import os

app = Flask(__name__)
CORS(app)  # allow frontend to access backend

# ===================== LOAD MODELS =====================
CROP_MODEL_PATH = os.path.join("models", "crop_model.joblib")
DISEASE_MODEL_PATH = os.path.join("models", "disease_model.joblib")

crop_model = joblib.load(CROP_MODEL_PATH)
disease_model = tf.keras.models.load_model(DISEASE_MODEL_PATH)

# ===================== HELPER FUNCTIONS =====================
def predict_crop_model(data):
    """
    data = {"cropType": "Food Grain", "soilType": "Loamy", "rainfall": 300}
    """
    crop_type = data.get("cropType", "")
    soil_type = data.get("soilType", "")
    rainfall = float(data.get("rainfall", 0))

    # Simple encoding (example only)
    crop_dict = {"Food Grain": 1, "Pulses": 2, "Oilseeds": 3, "Cash Crop": 4}
    soil_dict = {"Clay": 1, "Loamy": 2, "Sandy": 3, "Red": 4, "Black": 5}

    crop_val = crop_dict.get(crop_type, 0)
    soil_val = soil_dict.get(soil_type, 0)

    features = np.array([[crop_val, soil_val, rainfall]])
    predicted_crop = crop_model.predict(features)[0]
    return predicted_crop


def predict_disease_model(file):
    """
    Takes uploaded image, preprocesses, and predicts using CNN.
    """
    image = Image.open(io.BytesIO(file.read())).convert("RGB")
    image = image.resize((128, 128))
    img_array = np.array(image) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = disease_model.predict(img_array)
    predicted_class = np.argmax(prediction, axis=1)[0]

    # Example mapping (customize based on your model classes)
    classes = ["Healthy", "Blight", "Rust", "Leaf Spot"]
    result = classes[predicted_class]
    return result


# ===================== ROUTES =====================
@app.route("/predict_crop", methods=["POST"])
def predict_crop():
    data = request.get_json()
    crop = predict_crop_model(data)
    return jsonify({"recommended_crop": crop})


@app.route("/detect_disease", methods=["POST"])
def detect_disease():
    file = request.files["image"]
    result = predict_disease_model(file)
    return jsonify({"disease_result": result})


# ===================== MAIN =====================
if __name__ == "__main__":
    app.run(debug=True, port=5000)
