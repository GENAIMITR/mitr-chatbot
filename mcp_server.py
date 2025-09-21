# mcp_server.py
from flask import Flask, request, jsonify
from google.cloud import firestore
from google.cloud.firestore import SERVER_TIMESTAMP
import os

app = Flask(__name__)
db = firestore.Client()

@app.route("/mcp/add_message", methods=["POST"])
def add_message():
    try:
        data = request.json
        session_doc_ref = db.collection(data["persona"]).document(data["session_id"])
        session_doc_ref.set({"last_updated": SERVER_TIMESTAMP}, merge=True)
        messages_col_ref = session_doc_ref.collection("messages")
        messages_col_ref.add({
            "speaker": data["speaker"],
            "text": data["text"],
            "ts": SERVER_TIMESTAMP
        })
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"!!! ADD_MESSAGE ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/mcp/get_messages", methods=["POST"])
def get_messages():
    try:
        data = request.json
        limit = data.get("limit", 50)
        msgs_col = db.collection(data["persona"]).document(data["session_id"]).collection("messages")
        docs = msgs_col.limit(limit).stream()
        out = []
        for d in docs:
            doc_data = d.to_dict()
            if 'ts' in doc_data and hasattr(doc_data['ts'], 'isoformat'):
                doc_data['ts'] = doc_data['ts'].isoformat()
            out.append(doc_data)
        out.sort(key=lambda x: x.get('ts', ''))
        return jsonify({"result": out})
    except Exception as e:
        print(f"!!! GET_MESSAGES ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/mcp/get_sessions", methods=["POST"])
def get_sessions():
    try:
        data = request.json
        docs = db.collection(data["persona"]).stream()
        session_ids = [doc.id for doc in docs]
        return jsonify({"result": session_ids})
    except Exception as e:
        print(f"!!! GET_SESSIONS ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/mcp/clear_history", methods=["POST"])
def clear_history():
    try:
        data = request.json
        docs = db.collection(data["persona"]).document(data["session_id"]).collection("messages").stream()
        batch = db.batch()
        for doc in docs:
            batch.delete(doc.reference)
        batch.commit()
        if data["session_id"] != "default":
            db.collection(data["persona"]).document(data["session_id"]).delete()
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"!!! CLEAR_HISTORY ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- MODIFIED FUNCTION ---
@app.route("/mcp/add_persona_memory", methods=["POST"])
def add_persona_memory():
    try:
        data = request.json
        # All memories go to one common location
        mem = db.collection("persona_memories").document("common_memory").collection("entries")
        mem.add({
            "speaker": data["persona"], # Store which persona said it
            "text": data["text"],
            "ts": SERVER_TIMESTAMP
        })
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"!!! ADD_PERSONA_MEMORY ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- MODIFIED FUNCTION ---
@app.route("/mcp/get_persona_memory", methods=["POST"])
def get_persona_memory():
    try:
        data = request.json
        limit = data.get("limit", 10)
        # Fetch from the common memory location, ignoring the persona in the path
        mem_col = db.collection("persona_memories").document("common_memory").collection("entries")
        
        docs = mem_col.limit(limit).stream()
        entries = []
        for d in docs:
            entry_data = d.to_dict()
            if 'ts' in entry_data and hasattr(entry_data['ts'], 'isoformat'):
                entry_data['ts'] = entry_data['ts'].isoformat()
            entries.append(entry_data)
        
        entries.sort(key=lambda x: x.get('ts', ''), reverse=True)
        
        # Format the memory to include which persona said what
        result = "\n".join([f"{e.get('speaker', 'AI')}: {e.get('text', '')}" for e in entries])
        return jsonify({"result": result})
    except Exception as e:
        print(f"!!! GET_PERSONA_MEMORY ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8081)))