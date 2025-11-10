from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import os
import io
import numpy as np
from PIL import Image, ImageDraw
import onnxruntime as ort
import secrets
import random
import json
import time
from datetime import datetime
import base64

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# --- Configuração dos Modelos ONNX ---
IMG_SIZE = (224, 224)
providers = ['CPUExecutionProvider']
keras_session = ort.InferenceSession("Models/Modelo_Keras.onnx", providers=providers)
yolo_session = ort.InferenceSession("Models/Modelo_Yolov11.onnx", providers=providers)
topo_classifier_session = ort.InferenceSession("Models/Modelo_Topografia_Classifier.onnx", providers=providers)
keras_input_name = keras_session.get_inputs()[0].name
yolo_input_name = yolo_session.get_inputs()[0].name
topo_classifier_input_name = topo_classifier_session.get_inputs()[0].name

# --- Funções de Pré-processamento de Imagem ---
def preprocess_image(img, target_size=IMG_SIZE):
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img.resize(target_size)

def get_keras_input(img):
    img_array = np.array(img, dtype=np.float32)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
    return img_array

def get_yolo_input(img):
    img_array = np.array(img, dtype=np.float32)
    img_array = img_array.transpose(2, 0, 1)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
    return img_array

def generate_mock_gradcam(img):
    img_copy = img.convert("RGB").copy()  # Garante RGB
    draw = ImageDraw.Draw(img_copy)
    w, h = img_copy.size
    radius = min(w, h) // 6
    center = (w // 2, h // 2)

    # Cria overlay RGBA e combina com RGB
    overlay = Image.new('RGBA', img_copy.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.ellipse(
        (
            center[0] + random.randint(1, 30) - radius,
            center[1] + random.randint(1, 30) - radius,
            center[0] + random.randint(1, 30) + radius,
            center[1] + random.randint(1, 30) + radius
        ),
        outline=(255, 0, 0, 180),
        width=8
    )

    # Faz a fusão e converte explicitamente para RGB
    combined = Image.alpha_composite(img_copy.convert('RGBA'), overlay).convert('RGB')

    buffered = io.BytesIO()
    combined.save(buffered, format="JPEG")  # Agora seguro
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# --- Rotas ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/oftsys-cadastro-paciente")
def cadastro_paciente():
    return render_template("oftsys-cadastro-paciente.html")

@app.route("/artigo")
def artigo():
    return render_template("artigo.html")

@app.route("/oftsys", methods=["GET", "POST"])
def oftsys():
    if request.method == "POST":
        session['patient_data'] = {
            'nome': request.form.get('nome'),
            'nascimento': request.form.get('nascimento'),
            'sexo': request.form.get('sexo'),
            'prontuario': request.form.get('prontuario')
        }
        return render_template("oftsys.html")
    return redirect(url_for('cadastro_paciente'))

@app.route("/predict", methods=["POST"])
def predict():
    files = request.files.getlist("files[]")

    if not files or 'patient_data' not in session:
        return jsonify({"error": "Dados incompletos ou nenhuma imagem enviada."}), 400

    all_results = []

    try:
        for file in files:
            # --- Timestamp ---
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            start_time = time.time()

            img_bytes = io.BytesIO(file.read())
            img = Image.open(img_bytes)
            img = img.convert("RGB")
            processed_img = preprocess_image(img)

            # --- Verificação de topografia ---
            topo_input = get_keras_input(processed_img)
            topo_pred_value = topo_classifier_session.run(None, {topo_classifier_input_name: topo_input})[0][0][0]
            topo_threshold = 0.5

            if topo_pred_value < topo_threshold:
                all_results.append({
                    "filename": file.filename,
                    "status": "rejeitada",
                    "reason": "A imagem não foi identificada como uma topografia de córnea."
                })
                continue

            # --- Predição Keras ---
            keras_input = get_keras_input(processed_img)
            keras_pred_value = keras_session.run(None, {keras_input_name: keras_input})[0][0][0]

            threshold = 0.5
            if keras_pred_value >= threshold:
                predicted_class_keras = 1
                confidence_keras = float(keras_pred_value)
            else:
                predicted_class_keras = 0
                confidence_keras = 1.0 - float(keras_pred_value)

            # --- Predição YOLO ---
            yolo_input = get_yolo_input(processed_img)
            yolo_pred = yolo_session.run(None, {yolo_input_name: yolo_input})[0]

            inference_time = time.time() - start_time

            # --- Converter imagem original em base64 ---
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            encoded_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # --- Gerar Grad-CAM falso ---
            gradcam_encoded = generate_mock_gradcam(processed_img)

            # --- Resultado ---
            all_results.append({
                "filename": file.filename,
                "status": "analisada",
                "timestamp": timestamp,
                "inference_time": round(inference_time, 2),
                "uploaded_image": encoded_image,
                "gradcam_image": gradcam_encoded,
                "keras": {
                    "predicted_class": predicted_class_keras,
                    "confidence": confidence_keras
                },
                "yolo": {
                    "predicted_class": int(np.argmax(yolo_pred, axis=1)[0]),
                    "confidence": float(np.max(yolo_pred, axis=1)[0])
                }
            })
        session['ia_meta'] = [
            {
                "filename": r["filename"],
                "status": r["status"],
                "timestamp": r.get("timestamp"),
                "inference_time": r.get("inference_time"),
                "keras": r.get("keras"),
                "yolo": r.get("yolo")
            }
            for r in all_results
        ]

        patient_data = session.get('patient_data')
        return render_template("analises.html", patient=patient_data, results=all_results)

    except Exception as e:
        print(f"Ocorreu um erro durante a predição: {e}")
        return jsonify({"error": "Falha ao processar uma das imagens no servidor."}), 500


@app.route("/analises")
def analises():
    patient_data = session.get('patient_data')
    ia_meta = session.get('ia_meta')

    if not patient_data or not ia_meta:
        return redirect(url_for('cadastro_paciente'))

    return redirect(url_for('cadastro_paciente'))


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/produto")
def produto():
    return render_template("produto.html")

@app.route("/como-funciona")
def como_funciona():
    return render_template("como-funciona.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/recursos")
def recursos():
    return render_template("recursos.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or 'mensagem' not in data:
        return jsonify({"error": "Nenhuma mensagem recebida."}), 400

    user_message = data['mensagem'].lower()

    with io.open('static/chatbotHardCoded/chatbot.json', 'r', encoding='utf-8') as f:
        intents = json.load(f)

    for intent in intents['intents']:
        for pattern in intent['patterns']:
            if pattern.lower() in user_message:
                bot_response = random.choice(intent['responses'])
                return jsonify({"resposta": bot_response})

    bot_response = f"OFTBOT não reconhece: '{user_message}'"
    return jsonify({"resposta": bot_response})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=int(os.getenv("PORT", 5000)))
