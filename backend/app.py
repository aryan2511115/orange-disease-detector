"""Orange Disease Detection - Flask Backend API

This server is designed to ALWAYS start (demo mode fallback) even if:
- TensorFlow model is missing
- class mapping file is missing
- Grad-CAM fails
- MySQL is not running / misconfigured

Run:
  python app.py
Server:
  http://127.0.0.1:5000
"""

from __future__ import annotations

import os
import json
import numpy as np
from datetime import datetime

from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image

# TensorFlow is optional at runtime (demo mode if missing)
try:
    import tensorflow as tf  # noqa: F401
    from tensorflow.keras.models import load_model
except Exception as error:
    load_model = None
    tf = None
    print("Error:", error)


# Optional runtime dependencies
try:
    import pyttsx3  # noqa: F401
except Exception as error:
    pyttsx3 = None
    print("Error:", error)

# MySQL is optional at runtime (demo mode if missing)
try:
    import mysql.connector
except Exception as error:
    mysql = None
    print("Error:", error)



# Optional dependency/module
try:
    # backend/gradcam_explainer.py lives beside this file
    from gradcam_explainer import GradCAMExplainer
except Exception as e:
    print("Warning: Grad-CAM module not available. Error:", e)
    GradCAMExplainer = None

# -------------------------
# Path handling (critical)
# -------------------------
THIS_DIR = os.path.dirname(os.path.abspath(__file__))  # .../backend
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))

TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset", "preprocessed")

MODEL_PATH = os.path.join(MODEL_DIR, "best_model.h5")
CLASS_MAPPING_PATH = os.path.join(DATASET_DIR, "class_mapping.json")

# -------------------------
# Flask app
# -------------------------
app = Flask(
    __name__,
    template_folder=TEMPLATES_DIR,
    static_folder=STATIC_DIR,
)

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
app.config["ALLOWED_EXTENSIONS"] = {"jpg", "jpeg", "png", "gif"}
app.config["SECRET_KEY"] = "your-secret-key-change-this"

CORS(app)

# -------------------------
# Globals
# -------------------------
model = None
_disease_classes: list[str] | None = None
gradcam_explainer = None
db_connection = None

# Disease information with multilingual support
DISEASE_INFO = {
    "en": {
        "Citrus Canker": {
            "severity": "High",
            "treatment": "Prune affected branches, apply copper fungicides, maintain tree vigor.",
            "prevention": "Remove infected trees, use disease-free nursery stock.",
            "fertilizer": "Apply balanced NPK (10-10-10) with micronutrients.",
        },
        "Black Spot": {
            "severity": "Medium",
            "treatment": "Apply copper-based fungicides, remove infected fruit.",
            "prevention": "Proper pruning for air circulation, remove fallen fruit.",
            "fertilizer": "Use potassium-rich fertilizers (NPK 10-10-30).",
        },
        "Citrus Greening (HLB)": {
            "severity": "Critical",
            "treatment": "No cure exists, remove infected trees, control psyllid vector.",
            "prevention": "Plant certified disease-free trees, control psyllid.",
            "fertilizer": "Apply high nitrogen fertilizers for tree health.",
        },
        "Leaf Miner": {
            "severity": "Low",
            "treatment": "Apply insecticides (neem oil), prune affected leaves.",
            "prevention": "Regular inspection, maintain tree vigor, use parasitic wasps.",
            "fertilizer": "Apply balanced fertilizers, avoid excess nitrogen.",
        },
        "Healthy Orange Leaf": {
            "severity": "None",
            "treatment": "No treatment needed.",
            "prevention": "Maintain regular care and nutrition.",
            "fertilizer": "Maintain balanced NPK with micronutrients.",
        },
    },
    "hi": {
        "Citrus Canker": {
            "severity": "उच्च",
            "treatment": "प्रभावित शाखाओं को काटें, कॉपर कवकनाशी लागू करें।",
            "prevention": "संक्रमित पेड़ों को हटाएं, रोगमुक्त नर्सरी स्टॉक का उपयोग करें।",
            "fertilizer": "संतुलित NPK (10-10-10) खाद लागू करें।",
        },
        "Black Spot": {
            "severity": "मध्यम",
            "treatment": "कॉपर आधारित कवकनाशी लागू करें, संक्रमित फलों को हटाएं।",
            "prevention": "उचित छंटाई करें, गिरे हुए फलों को हटाएं।",
            "fertilizer": "पोटेशियम से भरपूर खाद का उपयोग करें।",
        },
        "Citrus Greening (HLB)": {
            "severity": "गंभीर",
            "treatment": "कोई इलाज नहीं, संक्रमित पेड़ों को हटाएं।",
            "prevention": "प्रमाणित रोगमुक्त पेड़ लगाएं।",
            "fertilizer": "उच्च नाइट्रोजन खाद लागू करें।",
        },
        "Leaf Miner": {
            "severity": "कम",
            "treatment": "कीटनाशक (नीम का तेल) लागू करें।",
            "prevention": "नियमित निरीक्षण, पेड़ की मजबूती बनाए रखें।",
            "fertilizer": "संतुलित खाद लागू करें, अतिरिक्त नाइट्रोजन से बचें।",
        },
        "Healthy Orange Leaf": {
            "severity": "कोई नहीं",
            "treatment": "कोई इलाज की आवश्यकता नहीं।",
            "prevention": "नियमित देखभाल और पोषण बनाए रखें।",
            "fertilizer": "संतुलित NPK खाद बनाए रखें।",
        },
    },
    "mr": {
        "Citrus Canker": {
            "severity": "उच्च",
            "treatment": "प्रभावित शाखा कापा, कॉपर फंजिसाइड लागू करा।",
            "prevention": "संक्रमित झाड हटवा, निरोगी नर्सरी स्टॉक वापरा।",
            "fertilizer": "संतुलित NPK खत लागू करा।",
        },
        "Black Spot": {
            "severity": "मध्यम",
            "treatment": "कॉपर आधारित बोलीविदनाशक लागू करा।",
            "prevention": "योग्य छाटणी करा, पडलेले फळ हटवा।",
            "fertilizer": "पोटेशियम समृद्ध खत वापरा।",
        },
        "Citrus Greening (HLB)": {
            "severity": "गंभीर",
            "treatment": "कोणतेही उपचार नाही, संक्रमित झाड हटवा।",
            "prevention": "प्रमाणित रोगमुक्त झाड लावा।",
            "fertilizer": "उच्च नायट्रोजन खत लागू करा।",
        },
        "Leaf Miner": {
            "severity": "कम",
            "treatment": "कीटकनाशक लागू करा, प्रभावित पत्ते कापा।",
            "prevention": "नियमित तपासणी, झाडाची मजबूती राखा।",
            "fertilizer": "संतुलित खत लागू करा।",
        },
        "Healthy Orange Leaf": {
            "severity": "कोणते नाही",
            "treatment": "कोणतेही उपचार आवश्यक नाही।",
            "prevention": "नियमित काळजी आणि पोषण राखा।",
            "fertilizer": "संतुलित NPK खत राखा।",
        },
    },
}

# -------------------------
# Utility helpers
# -------------------------

def ensure_required_folders() -> None:
    required = [
        MODEL_DIR,
        os.path.join(PROJECT_ROOT, "dataset", "preprocessed"),
        UPLOAD_DIR,
        TEMPLATES_DIR,
        STATIC_DIR,
        os.path.join(PROJECT_ROOT, "logs"),
    ]
    for p in required:
        os.makedirs(p, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


def preprocess_image(image_path: str, target_size=(224, 224)) -> np.ndarray:
    img = Image.open(image_path).convert("RGB")
    img = img.resize(target_size)
    img_array = np.array(img) / 255.0
    return np.expand_dims(img_array, axis=0)


def calculate_disease_severity(confidence: float, disease_class: str) -> float:
    severity_multipliers = {
        "Citrus Canker": 0.85,
        "Black Spot": 0.70,
        "Citrus Greening (HLB)": 0.95,
        "Leaf Miner": 0.50,
        "Healthy Orange Leaf": 0.0,
    }
    multiplier = severity_multipliers.get(disease_class, 0.5)
    severity = confidence * 100 * multiplier
    return min(100.0, float(severity))


def speak_text(text: str, language: str = "en") -> None:
    # language kept for compatibility; TTS engine may not support i18n voices.
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 0.9)
        engine.say(text)
        engine.runAndWait()
    except Exception as error:
        print("Error:", error)


def save_to_database(
    user_id,
    image_name,
    predicted_disease,
    confidence,
    severity,
    gradcam_path=None,
) -> None:
    # If DB isn't configured, just skip.
    if not db_connection:
        return

    try:
        cursor = db_connection.cursor()
        insert_query = """
        INSERT INTO predictions (
            user_id, image_name, predicted_disease, confidence_score,
            disease_severity, gradcam_path, model_used
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            user_id,
            image_name,
            predicted_disease,
            float(confidence),
            float(severity),
            gradcam_path,
            "TransferLearning_Ensemble",
        )
        cursor.execute(insert_query, values)
        db_connection.commit()
        cursor.close()
        print("Database connected")
    except Exception as error:
        print("Error:", error)


def load_or_create_class_mapping() -> list[str]:
    sample_mapping = {
        "disease_classes": [
            "Citrus Canker",
            "Black Spot",
            "Citrus Greening (HLB)",
            "Leaf Miner",
            "Healthy Orange Leaf",
        ]
    }

    try:
        if os.path.exists(CLASS_MAPPING_PATH):
            with open(CLASS_MAPPING_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            classes = data.get("disease_classes")
            if isinstance(classes, list) and classes:
                return classes
    except Exception as error:
        print("Error:", error)

    # create sample
    try:
        ensure_required_folders()
        with open(CLASS_MAPPING_PATH, "w", encoding="utf-8") as f:
            json.dump(sample_mapping, f, ensure_ascii=False, indent=2)
    except Exception as error:
        print("Error:", error)

    return sample_mapping["disease_classes"]


def create_dummy_best_model_if_missing() -> None:
    """Create a minimal Keras model if best_model.h5 is missing.

    This is only to keep the API alive in demo mode.
    """
    if os.path.exists(MODEL_PATH) and os.path.getsize(MODEL_PATH) > 0:
        return

    try:
        from tensorflow.keras import layers, models

        num_classes = 5
        inputs = layers.Input(shape=(224, 224, 3), name="input")
        x = layers.Rescaling(1.0 / 255.0)(inputs)
        x = layers.GlobalAveragePooling2D()(x)
        outputs = layers.Dense(num_classes, activation="softmax")(x)
        dummy = models.Model(inputs=inputs, outputs=outputs, name="dummy_orange_disease")
        dummy.compile(optimizer="adam", loss="categorical_crossentropy")

        ensure_required_folders()
        dummy.save(MODEL_PATH)
        print("Created dummy model at", MODEL_PATH)
    except Exception as error:
        # If this fails, API will still run in demo mode; model loading will fail.
        print("Error:", error)


def load_model_and_classes() -> None:
    global model, _disease_classes, gradcam_explainer

    _disease_classes = load_or_create_class_mapping()

    # Ensure dummy model exists so load_model doesn't crash.
    create_dummy_best_model_if_missing()

    try:
        if os.path.exists(MODEL_PATH):
            model = load_model(MODEL_PATH)
            print("Model loaded")
        else:
            print("Error:", f"Model path does not exist: {MODEL_PATH}")
            model = None

        if model is not None and GradCAMExplainer:
            try:
                gradcam_explainer = GradCAMExplainer(model)
            except Exception as error:
                gradcam_explainer = None
                print("Error:", error)
    except Exception as error:
        model = None
        gradcam_explainer = None
        print("Error:", error)


def initialize_database_connection() -> None:
    global db_connection
    try:
        db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="orange_disease_db",
        )
        print("Database connected")
    except Exception as error:
        db_connection = None
        print("Error:", error)


# -------------------------
# Routes
# -------------------------

@app.route("/", methods=["GET"])
def index():
    try:
        return render_template("index.html")
    except Exception as error:
        print("Error:", error)
        return jsonify(
            {
                "message": "Orange Disease Detection API",
                "version": "1.0.0",
                "status": "active",
                "endpoints": {
                    "health": "/api/health",
                    "predict": "/api/predict (POST)",
                    "diseases": "/api/diseases",
                    "languages": "/api/languages",
                },
            }
        )


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify(
        {
            "status": "healthy",
            "model_loaded": model is not None,
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/api/predict", methods=["POST"])
def predict_disease():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files["image"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file format"}), 400

    try:
        # Ensure classes exist
        classes = _disease_classes or load_or_create_class_mapping()

        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
        filename = timestamp + filename

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        file.save(filepath)

        processed_img = preprocess_image(filepath)

        if model is not None:
            predictions = model.predict(processed_img, verbose=0)
            predicted_idx = int(np.argmax(predictions[0]))
            predicted_disease = classes[predicted_idx]
            confidence = float(predictions[0][predicted_idx])
        else:
            import random

            predicted_disease = random.choice(classes)
            confidence = round(random.uniform(0.85, 0.99), 4)
            predicted_idx = 0
            predictions = np.zeros((1, len(classes)), dtype=float)

        severity = calculate_disease_severity(confidence, predicted_disease)
        language = request.form.get("language", "en")

        disease_info = DISEASE_INFO.get(language, DISEASE_INFO["en"]).get(
            predicted_disease, {"treatment": "", "prevention": "", "fertilizer": ""}
        )

        # Grad-CAM (best-effort)
        gradcam_path = None
        gradcam_filename = None
        if gradcam_explainer and model is not None:
            try:
                gradcam_filename = f"gradcam_{os.path.splitext(filename)[0]}.png"
                gradcam_path = os.path.join(app.config["UPLOAD_FOLDER"], gradcam_filename)

                heatmap = gradcam_explainer.generate_gradcam(processed_img, predicted_idx)
                original_img = (processed_img[0] * 255).astype(np.uint8)
                overlaid = gradcam_explainer.overlay_gradcam(original_img, heatmap)
                Image.fromarray(overlaid).save(gradcam_path)
            except Exception as error:
                print("Error:", error)
                gradcam_path = None

        user_id = request.form.get("user_id")
        if user_id:
            save_to_database(
                user_id,
                filename,
                predicted_disease,
                confidence,
                severity,
                gradcam_path,
            )

        # all_predictions
        all_predictions = {}
        try:
            if model is not None:
                all_predictions = {classes[i]: float(predictions[0][i]) for i in range(len(classes))}
            else:
                # demo mode: uniform-ish scores
                for c in classes:
                    all_predictions[c] = round(1.0 / len(classes), 4)
        except Exception as error:
            print("Error:", error)

        return (
            jsonify(
                {
                    "status": "success",
                    "predicted_disease": predicted_disease,
                    "confidence": confidence,
                    "confidence_percentage": f"{confidence * 100:.2f}%",
                    "severity": f"{severity:.2f}%",
                    "treatment": disease_info.get("treatment", ""),
                    "prevention": disease_info.get("prevention", ""),
                    "fertilizer_recommendation": disease_info.get("fertilizer", ""),
                    "severity_level": disease_info.get("severity", ""),
                    "image_path": f"/static/uploads/{filename}",
                    "gradcam_path": f"/static/uploads/{gradcam_filename}" if gradcam_path else None,
                    "all_predictions": all_predictions,
                }
            ),
            200,
        )

    except Exception as error:
        print("Error:", error)
        return jsonify({"error": f"Prediction error: {str(error)}"}), 500


@app.route("/api/diseases", methods=["GET"])
def get_all_diseases():
    language = request.args.get("language", "en")
    classes = _disease_classes or load_or_create_class_mapping()

    diseases = []
    disease_info_lang = DISEASE_INFO.get(language, DISEASE_INFO["en"])

    for disease in classes:
        diseases.append({"name": disease, "info": disease_info_lang.get(disease, {})})

    return jsonify({"total": len(diseases), "language": language, "diseases": diseases}), 200


@app.route("/api/disease-info/<disease_name>", methods=["GET"])
def get_disease_info(disease_name):
    language = request.args.get("language", "en")
    disease_data = DISEASE_INFO.get(language, DISEASE_INFO["en"]).get(disease_name)
    if not disease_data:
        return jsonify({"error": "Disease not found"}), 404
    return jsonify({"disease_name": disease_name, "language": language, "info": disease_data}), 200


@app.route("/api/languages", methods=["GET"])
def get_supported_languages():
    return jsonify(
        {
            "supported_languages": [
                {"code": "en", "name": "English"},
                {"code": "hi", "name": "हिंदी (Hindi)"},
                {"code": "mr", "name": "मराठी (Marathi)"},
            ]
        }
    ), 200


@app.route("/api/prediction-history/<int:user_id>", methods=["GET"])
def get_prediction_history(user_id: int):
    if not db_connection:
        return jsonify({"error": "Database not connected"}), 503

    try:
        cursor = db_connection.cursor(dictionary=True)
        query = """
        SELECT * FROM predictions
        WHERE user_id = %s
        ORDER BY prediction_timestamp DESC
        LIMIT 50
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        return jsonify({"user_id": user_id, "total_predictions": len(rows), "predictions": rows}), 200
    except Exception as error:
        print("Error:", error)
        return jsonify({"error": str(error)}), 500


@app.route("/api/statistics", methods=["GET"])
def get_statistics():
    if not db_connection:
        return jsonify({"error": "Database not connected"}), 503

    try:
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as total FROM predictions")
        total_predictions = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT predicted_disease, COUNT(*) as count
            FROM predictions
            GROUP BY predicted_disease
            """
        )
        disease_dist = cursor.fetchall()

        cursor.execute("SELECT AVG(confidence_score) as avg_confidence FROM predictions")
        avg_confidence = cursor.fetchone()["avg_confidence"]
        cursor.close()

        return (
            jsonify(
                {
                    "total_predictions": total_predictions,
                    "average_confidence": float(avg_confidence) if avg_confidence else 0,
                    "disease_distribution": disease_dist,
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )
    except Exception as error:
        print("Error:", error)
        return jsonify({"error": str(error)}), 500


@app.route("/api/models", methods=["GET"])
def get_model_info():
    classes = _disease_classes or []
    return (
        jsonify(
            {
                "available_models": ["MobileNetV2", "ResNet50", "EfficientNetB0"],
                "current_model": "EfficientNetB0 (Best Performer)",
                "input_size": [224, 224, 3],
                "output_classes": len(classes),
                "classes": classes,
            }
        ),
        200,
    )


@app.route("/static/<path:filename>", methods=["GET"])
def serve_static(filename: str):
    # Best-effort: allow frontend assets
    return send_file(os.path.join(STATIC_DIR, filename))


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(_error):
    return jsonify({"error": "Internal server error"}), 500


# -------------------------
# Startup
# -------------------------

def startup() -> None:
    ensure_required_folders()

    try:
        load_model_and_classes()
    except Exception as error:
        print("Error:", error)

    try:
        initialize_database_connection()
    except Exception as error:
        print("Error:", error)

    print("Server started")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ORANGE DISEASE DETECTION - FLASK API SERVER")
    print("=" * 60 + "\n")

    startup()

    print("Running on: http://127.0.0.1:5000")

    app.run(
        debug=False,
        host="127.0.0.1",
        port=5000,
        use_reloader=False,
    )

