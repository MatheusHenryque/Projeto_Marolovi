from flask import Flask, render_template
# from llama_index.llms.groq import Groq
# from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# from llama_index.core.memory import ChatSummaryMemoryBuffer
# from llama_index.core.vector_stores import SimpleVectorStore
# from llama_index.core import Settings
# from dotenv import load_dotenv
import os

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

@app.route("/analises")
def analises():
    return render_template("analises.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
