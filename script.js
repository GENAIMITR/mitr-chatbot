// script.js
let currentPersona = "Lucy";
let currentMode = "text";
let currentSessionId = "default";
let isRecording = false;
let mediaRecorder;
let audioChunks = [];

const API_BASE = "/api";

const personaDescriptions = {
  Lucy: "Gentle, sweet, comforting, soft-spoken, timid, welcoming, patient, good listener 💕",
  Suzanne:
    "Funny, silly, playful, comforting, jovial, empathetic, lighthearted, witty 😂",
  Lexi: "Wise, thoughtful, smart, decisive, self-aware, articulate, logical 🌿",
  Roxy: "Bold, confident, badass, girl's girl, supportive, courageous, outgoing 🔥",
};

window.onload = function () {
  const userInput = document.getElementById("user-input");
  // Feature: Send message on "Enter" key press
  userInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      event.preventDefault();
      sendMessage();
    }
  });

  selectPersona(currentPersona); // Load default persona and session
  setMode("text"); // Ensure text mode is the default view
};

function selectPersona(persona) {
  currentPersona = persona;
  currentSessionId = "default"; // Reset to default session for the new persona

  document
    .querySelectorAll(".persona-option")
    .forEach((o) =>
      o.classList.toggle("active", o.dataset.persona === persona)
    );
  document.getElementById("persona-description").textContent =
    personaDescriptions[persona];
  document.body.className = `${persona.toLowerCase()}-theme`;

  loadHistory();
}

function setMode(mode) {
  currentMode = mode;
  document
    .getElementById("text-mode-btn")
    .classList.toggle("active-mode", mode === "text");
  document
    .getElementById("voice-mode-btn")
    .classList.toggle("active-mode", mode === "voice");
  document.getElementById("user-input").style.display =
    mode === "text" ? "block" : "none";
  document.getElementById("send-btn").style.display =
    mode === "text" ? "flex" : "none";
  document.getElementById("mic-btn").style.display =
    mode === "voice" ? "flex" : "none";
}

function sendMessage() {
  const input = document.getElementById("user-input");
  const message = input.value.trim();
  if (!message) return;

  addMessage(message, "user");
  input.value = "";

  fetch(`${API_BASE}/send_message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      persona: currentPersona,
      session_id: currentSessionId,
    }),
  })
    .then((res) => {
      if (!res.ok) {
        // If server returns an error status (like 500), handle it
        return res.json().then((err) => Promise.reject(err));
      }
      return res.json();
    })
    .then((data) => {
      if (data.reply) {
        addMessage(data.reply, currentPersona);
      }
    })
    .catch((error) => {
      console.error("Error sending message:", error);
      const errorMessage = error.message || "An unknown error occurred.";
      alert(`A backend error occurred:\n\n${errorMessage}`);
      document.querySelector(".user-message:last-child").remove();
    });
}

function addMessage(text, sender) {
  const container = document.getElementById("chat-messages");
  const messageDiv = document.createElement("div");
  if (sender === "user") {
    messageDiv.className = "user-message";
    messageDiv.textContent = text;
  } else {
    messageDiv.className = "bot-message";
    messageDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
  }
  container.appendChild(messageDiv);
  container.scrollTop = container.scrollHeight;
}

function loadHistory() {
  fetch(`${API_BASE}/get_history`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      persona: currentPersona,
      session_id: currentSessionId,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      const chatBox = document.getElementById("chat-messages");
      chatBox.innerHTML = "";
      if (data.messages) {
        data.messages.forEach((msg) => addMessage(msg.text, msg.speaker));
      }
    });
}

function deleteCurrentSession() {
  if (!currentSessionId || currentSessionId === "default") {
    alert(
      "The 'default' session cannot be deleted. Please use the Session History view to delete named sessions."
    );
    return;
  }
  deleteSessionFromList(currentSessionId);
}

function showSessionHistory() {
  fetch(`${API_BASE}/get_sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ persona: currentPersona }),
  })
    .then((res) => res.json())
    .then((data) => {
      const chatBox = document.getElementById("chat-messages");
      // This is the corrected line: It now looks for data.sessions
      const sessionList =
        data.sessions && data.sessions.length > 0
          ? data.sessions
              .map(
                (id) => `
                <li class="session-item">
                    <span class="session-item-name" onclick="loadSession('${id}')">${id}</span>
                    ${
                      id !== "default"
                        ? `<button class="delete-session-btn" onclick="deleteSessionFromList('${id}')" title="Delete session"><i class="fas fa-trash-alt"></i></button>`
                        : ""
                    }
                </li>
              `
              )
              .join("")
          : "<li>No saved sessions for this persona.</li>";
      chatBox.innerHTML = `
            <div class="session-list-container">
                <h3>Session History for ${currentPersona}</h3>
                <ul class="session-list">
                    ${sessionList}
                </ul>
                <button class="mode-btn new-session-btn" onclick="createNewSession()">
                    <i class="fas fa-plus-circle"></i> Start New Session
                </button>
            </div>
        `;
    });
}

function deleteSessionFromList(sessionId) {
  if (
    confirm(
      `Are you sure you want to delete the session '${sessionId}'? This cannot be undone.`
    )
  ) {
    fetch(`${API_BASE}/clear_history`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ persona: currentPersona, session_id: sessionId }),
    })
      .then((res) => {
        if (!res.ok) {
          return res.json().then((err) => Promise.reject(err));
        }
        return res.json();
      })
      .then(() => {
        if (currentSessionId === sessionId) {
          currentSessionId = "default";
          loadHistory();
        }
        showSessionHistory();
      })
      .catch((error) => {
        console.error("Error deleting session:", error);
        const errorMessage = error.message || "An unknown error occurred.";
        alert(`A backend error occurred while deleting:\n\n${errorMessage}`);
      });
  }
}

function loadSession(sessionId) {
  currentSessionId = sessionId;
  loadHistory();
}

function createNewSession() {
  const newSessionName = prompt(
    "Enter a name for the new session:",
    `session-${Date.now()}`
  );
  if (
    newSessionName &&
    newSessionName.trim() !== "" &&
    newSessionName.trim() !== "default"
  ) {
    currentSessionId = newSessionName.trim().replace(/[^a-zA-Z0-9-_]/g, "");
    loadHistory();
  } else {
    alert(
      "Invalid session name. Please use a different name and do not use 'default'."
    );
  }
}

async function toggleRecording() {
  if (isRecording) {
    mediaRecorder.stop();
  } else {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      isRecording = true;
      document.getElementById("mic-btn").classList.add("recording");
      audioChunks = [];
      mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = () => {
        isRecording = false;
        document.getElementById("mic-btn").classList.remove("recording");
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        sendAudioToServer(audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
    } catch (error) {
      console.error("Error accessing microphone:", error);
      alert(
        "Could not access the microphone. Please check your browser permissions."
      );
    }
  }
}

function sendAudioToServer(audioBlob) {
  const formData = new FormData();
  formData.append("audio_file", audioBlob, "recording.webm");
  addMessage("...listening...", "user");
  fetch(`${API_BASE}/transcribe_audio`, { method: "POST", body: formData })
    .then((res) => res.json())
    .then((data) => {
      document.querySelector(".user-message:last-child").remove();
      if (data.text && data.text.trim() !== "") {
        const textToSendMessage = data.text;
        const input = document.getElementById("user-input");
        input.value = textToSendMessage;
        sendMessage();
      } else {
        addMessage("Sorry, I couldn't hear anything.", currentPersona);
      }
    })
    .catch((error) => {
      console.error("Error transcribing audio:", error);
      document.querySelector(".user-message:last-child").remove();
      addMessage(
        "Sorry, there was an error with transcription.",
        currentPersona
      );
    });
}
