from flask import Flask, render_template
# from llama_index.llms.groq import Groq
# from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# from llama_index.core.memory import ChatSummaryMemoryBuffer
# from llama_index.core.vector_stores import SimpleVectorStore
# from llama_index.core import Settings
# from dotenv import load_dotenv
import os
import io
import numpy as np
from PIL import Image
from flask import Flask, request, jsonify, render_template
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from ultralytics import YOLO
import torch

IMG_SIZE = (224, 224)
keras_model = load_model("Models/Modelo_Keras_Improved.h5")
yolo_model = YOLO("Models/Modelo_Yolov11_Improve_Final.pt")

def preprocess_image_keras(img, target_size=IMG_SIZE):
    if img.mode != "RGB":
        img = img.convert("RGB")
    img = img.resize(target_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
    return img_array

app = Flask(__name__)
'''load_dotenv()

def init_chat_engine():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("API_KEY não encontrada no ambiente. Verifique o .env")

    embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")
    llm = Groq(model="llama3-8b-8192", api_key=api_key)

    Settings.embed_model = embed_model
    Settings.llm = llm

    memory = ChatSummaryMemoryBuffer(llm=llm, token_limit=512)
    documents = SimpleDirectoryReader("./documentos").load_data()
    vector_store = SimpleVectorStore()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

    return index.as_chat_engine(
        chat_mode="context",
        memory=memory,
        system_prompt=(
            "Você é um assistente especializado em Ceratocone. "
            "Responda com precisão sobre a doença, tratamentos, cirurgias, colírios "
            "e como a tecnologia pode ajudar no diagnóstico."
        )
    )

chat_engine = init_chat_engine()'''

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

'''@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    pergunta = data.get("mensagem", "")
    if not pergunta:
        return jsonify({"resposta": "Por favor, envie uma pergunta válida."})

    resposta = chat_engine.chat(pergunta).response
    return jsonify({"resposta": resposta}) '''

@app.route("/oftsys")
def oftsys():
    return render_template("oftsys.html")

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada"}), 400

    file = request.files["file"]
    img = Image.open(io.BytesIO(file.read()))

    # ======== Predição Keras =========
    keras_input = preprocess_image_keras(img)
    keras_pred = keras_model.predict(keras_input, verbose=0)
    keras_confidence = float(np.max(keras_pred))
    keras_class = int(np.argmax(keras_pred))

    # ======== Predição YOLOv11 =========
    img_resized = img.resize(IMG_SIZE)
    yolo_result = yolo_model(img_resized, imgsz=224, verbose=False)[0]
    yolo_class = int(torch.argmax(yolo_result.probs.data).item())
    yolo_confidence = float(torch.max(yolo_result.probs.data).item())

    return jsonify({
    "keras": {
        "predicted_class": keras_class,
        "confidence": keras_confidence
    },
    "yolo": {
        "predicted_class": yolo_class,
        "confidence": yolo_confidence
    }
    })

@app.route("/analises")
def analises():
    return render_template("analises.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
