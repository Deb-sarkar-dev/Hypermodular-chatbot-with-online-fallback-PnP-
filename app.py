from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_engine import RAGEngine

app = Flask(__name__)
CORS(app)

# Initialize RAGEngine
rag = RAGEngine(model_name="llama3.2")

@app.route('/ingest', methods=['POST'])
def ingest():
    data = request.json
    url = data.get('url', 'unknown')
    if url.startswith('file://'):
        domain = 'localhost'
    else:
        domain = url.split('/')[2] if '//' in url else url
    content = data.get('content', '')
    
    if not content:
        return jsonify({"status": "error", "message": "No content provided"}), 400
        
    success = rag.ingest_content(domain, url, content)
    return jsonify({"status": "success", "message": "Content ingested successfully."})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    url = data.get('url', 'unknown')
    if url.startswith('file://'):
        domain = 'localhost'
    else:
        domain = url.split('/')[2] if '//' in url else url
    message = data.get('message', '')
    
    if not message:
        return jsonify({"status": "error", "message": "No message provided"}), 400
        
    response, source = rag.generate_response(domain, message)
    return jsonify({"response": response, "source": source})

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    url = data.get('url', 'unknown')
    if url.startswith('file://'):
        domain = 'localhost'
    else:
        domain = url.split('/')[2] if '//' in url else url
    
    query = data.get('query')
    response = data.get('response')
    rating = data.get('rating') # 'positive' or 'negative'
    
    if rating == 'positive':
        # Learn from positive feedback! Store the interaction.
        rag.store_learned_interaction(domain, query, response, source_type="user_feedback")
        return jsonify({"status": "success", "message": "Thanks! I'll remember this for next time."})
    else:
        # Don't learn, maybe log it for admin review in a real app
        return jsonify({"status": "success", "message": "Thanks for the feedback. I won't use this response again."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
