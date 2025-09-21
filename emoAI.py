import cgi
import json
import os
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import google.generativeai as genai
from google.cloud import speech, texttospeech

# -----------------------------
# CONFIG
# -----------------------------
# API Key has been added
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
stt_client = speech.SpeechClient()
tts_client = texttospeech.TextToSpeechClient()

# -----------------------------
# Personas
# -----------------------------
personality_styles = {
    "Lucy": "gentle, sweet, comforting, soft-spoken, timid, welcoming, patient, good listener 💕",
    "Suzanne": "funny, silly, playful, comforting, jovial, empathetic, lighthearted, witty 😂",
    "Lexi": "wise, thoughtful, smart, decisive, self-aware, articulate, logical  🌿",
    "Roxy": "bold, confident, badass, girl's girl, supportive, courageous, outgoing 🔥"
}

# -----------------------------
# Data Helpers (using MCP Server)
# -----------------------------
def add_message(persona, session_id, speaker, text):
    try:
        response = requests.post(f"{MCP_SERVER_URL}/mcp/add_message", json={
            "persona": persona, "session_id": session_id, "speaker": speaker, "text": text
        })
        if response.status_code != 200:
            return response.json()
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_messages(persona, session_id, limit=50):
    try:
        response = requests.post(f"{MCP_SERVER_URL}/mcp/get_messages", json={
            "persona": persona, "session_id": session_id, "limit": limit
        })
        response.raise_for_status()
        return response.json().get("result", [])
    except Exception as e:
        print(f"Error calling MCP for get_messages: {e}")
        return []

def clear_history(persona, session_id):
    try:
        requests.post(f"{MCP_SERVER_URL}/mcp/clear_history", json={"persona": persona, "session_id": session_id})
    except Exception as e:
        print(f"Error calling MCP for clear_history: {e}")

def get_sessions(persona):
    try:
        response = requests.post(f"{MCP_SERVER_URL}/mcp/get_sessions", json={"persona": persona})
        response.raise_for_status()
        return response.json().get("result", [])
    except Exception as e:
        print(f"Error calling MCP for get_sessions: {e}")
        return []

def add_persona_memory(persona, text):
    try:
        requests.post(f"{MCP_SERVER_URL}/mcp/add_persona_memory", json={"persona": persona, "text": text})
    except Exception as e:
        print(f"Error calling MCP for add_persona_memory: {e}")

def get_persona_memory(persona, limit=10):
    try:
        response = requests.post(f"{MCP_SERVER_URL}/mcp/get_persona_memory", json={"persona": persona, "limit": limit})
        response.raise_for_status()
        return response.json().get("result", "")
    except Exception as e:
        print(f"Error calling MCP for get_persona_memory: {e}")
        return ""

# -----------------------------
# AI Logic (Modified for Shared Memory)
# -----------------------------
def generate_reply(user_text, persona, session_id):
    try:
        print(f"--- Generating reply for persona: {persona}, session: {session_id} ---")
        style = personality_styles.get(persona, "friendly and supportive")
        history = get_messages(persona, session_id, limit=20)
        history_text = "\n".join([f"{m.get('speaker', 'unknown')}: {m.get('text', '')}" for m in history])
        
        # This function now gets the shared memory
        persona_mem = get_persona_memory(persona) 

        # The prompt is updated to reflect the shared memory
        prompt = (
            f"You are {persona}, {style}. Speak as yourself only.\n\n"
            f"This is a shared memory log from all AI personas:\n{persona_mem}\n\n"
            f"Group chat so far:\n{history_text}\n"
            f"User just said: {user_text}\n"
            "Reply in 2–3 sentences."
        )

        print("--- Sending prompt to Gemini ---")
        response = model.generate_content(prompt)
        print("--- Received response from Gemini ---")
        return response.text.strip()
    except Exception as e:
        print("!!!!!!!!!!!!!! AN ERROR OCCURRED !!!!!!!!!!!!!!")
        print(f"Error details: {e}")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return "I'm sorry, I encountered an error and couldn't think of a reply."

# -----------------------------
# Audio Processing
# -----------------------------
def speech_to_text_bytes(audio_bytes):
    if not audio_bytes: return ""
    audio = speech.RecognitionAudio(content=audio_bytes)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        sample_rate_hertz=48000,
        language_code="en-US"
    )
    try:
        response = stt_client.recognize(config=config, audio=audio)
        return response.results[0].alternatives[0].transcript if response.results else ""
    except Exception as e:
        return f"Speech-to-text error: {e}"

# -----------------------------
# HTTP Server Class
# -----------------------------
class ChatbotHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self): self._set_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._set_headers(200, "text/html")
            with open("index.html", "rb") as f: self.wfile.write(f.read())
        elif parsed.path == "/styles.css":
            self._set_headers(200, "text/css")
            with open("styles.css", "rb") as f: self.wfile.write(f.read())
        elif parsed.path == "/script.js":
            self._set_headers(200, "application/javascript")
            with open("script.js", "rb") as f: self.wfile.write(f.read())
        else:
            self._set_headers(404); self.wfile.write(b"Not Found")

    def do_POST(self):
        content_type = self.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body.decode())

            if self.path == "/api/send_message":
                text = data.get("message", "").strip()
                persona = data.get("persona")
                session_id = data.get("session_id")
                result = add_message(persona, session_id, "user", text)
                if result.get("status") == "error":
                    self._set_headers(500)
                    self.wfile.write(json.dumps(result).encode())
                    return
                bot_reply = generate_reply(text, persona, session_id)
                add_message(persona, session_id, persona, bot_reply)
                add_persona_memory(persona, bot_reply)
                self._set_headers()
                self.wfile.write(json.dumps({"status": "success", "reply": bot_reply}).encode())
                return

            if self.path == "/api/get_history":
                msgs = get_messages(data.get("persona"), data.get("session_id"))
                self._set_headers()
                self.wfile.write(json.dumps({"status": "success", "messages": msgs}).encode())
                return
            
            if self.path == "/api/clear_history":
                clear_history(data.get("persona"), data.get("session_id"))
                self._set_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode())
                return
            
            if self.path == "/api/get_sessions":
                sessions = get_sessions(data.get("persona"))
                self._set_headers()
                self.wfile.write(json.dumps({"status": "success", "sessions": sessions}).encode())
                return
        
        if 'multipart/form-data' in content_type:
            if self.path == "/api/transcribe_audio":
                ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                fields = cgi.parse_multipart(self.rfile, pdict)
                audio_bytes = fields.get('audio_file')[0]
                text = speech_to_text_bytes(audio_bytes)
                self._set_headers()
                self.wfile.write(json.dumps({'status': 'success', 'text': text}).encode())
                return
            
        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Not Found"}).encode())

# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), ChatbotHandler)
    print(f"Server started at http://0.0.0.0:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()
