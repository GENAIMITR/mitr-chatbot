# MITR - An Empathetic AI Companion

MITR is a web-based, multi-persona AI chatbot designed to provide empathetic and context-aware conversations. It leverages a modern microservice architecture and Google's Generative AI to create a persistent and personalized user experience.



## Key Features

- **Multi-Persona System:** Switch between four distinct AI personalities (Lucy, Suzanne, Lexi, and Roxy), each with a unique style.
- **Persistent Session History:** Conversations are saved per-persona. Users can create new sessions, load past conversations, and delete old ones.
- **Client-Side Voice Mode:** A fully functional voice-to-text mode that uses the browser's microphone for real-time transcription.
- **Shared AI Memory:** All personas contribute to and learn from a common memory pool, allowing for richer, context-aware interactions over time.
- **Modern, Responsive UI:** A stylish and animated user interface featuring a persona selection carousel.

---

## Technology Stack

### Frontend
-   **HTML5, CSS3, & JavaScript:** Core technologies for the modern and interactive web interface.
-   **Tailwind CSS:** For modern, responsive, and utility-first styling.
-   **Swiper.js:** A powerful library used to create the animated, touch-enabled persona selection carousel.

### Backend (Microservice Architecture)
-   **Docker & Docker Compose:** For containerizing the application into portable services and managing the multi-service environment.
-   **Python:** The core language for all server-side logic and API integrations.
-   **Chatbot Service (`emoAI.py`):** A lightweight Python server that serves the frontend and handles AI and voice transcription logic.
-   **Data Service (`mcp_server.py`):** A robust Flask & Gunicorn API dedicated to all database operations.

### Cloud & AI Services (Google Cloud Platform)
-   **Google Gemini 1.5 Flash:** The core AI model for generating empathetic replies.
-   **Google Cloud Speech-to-Text:** For real-time, high-accuracy voice transcription.
-   **Google Cloud Firestore:** A scalable NoSQL database used to store all user sessions and shared AI memories.
-   **(Optional) Vertex AI & Natural Language API:** The platform is built to easily integrate further Google Cloud AI services.

---

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

You need to have the following software installed:
-   [Docker & Docker Compose](https://www.docker.com/products/docker-desktop/)
-   [Google Cloud SDK (`gcloud`)](https://cloud.google.com/sdk/docs/install)

### Configuration

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-name>
    ```

2.  **Google Cloud Setup:**
    -   Create a new project in the [Google Cloud Console](https://console.cloud.google.com/).
    -   Make sure **Billing** is enabled for your project.
    -   Enable the following APIs for your project: **Cloud Firestore API**, **Cloud Speech-to-Text API**, and **Vertex AI API**.

3.  **Create a Service Account:**
    -   In your Google Cloud project, navigate to **IAM & Admin > Service Accounts**.
    -   Click **+ CREATE SERVICE ACCOUNT**.
    -   Give it a name (e.g., `mitr-chatbot-sa`) and grant it the **Owner** role for simplicity during development.
    -   Create the account, go to the **Keys** tab, click **Add Key > Create new key**, select **JSON**, and create it.
    -   A JSON file will be downloaded. Rename this file to `ttsbot-471404-39e4ea704298.json` and place it in the root of your project folder.

4.  **Get Your Gemini API Key:**
    -   Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and create a new API key.
    -   Copy this key.

5.  **Create a Local Environment File:**
    -   In your project folder, create a new file named `.env`.
    -   Copy the content below into the `.env` file and paste your Gemini API key.
    ```env
    # .env
    # Paste your Gemini API key here
    GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxx
    ```

---

## Running Locally

1.  Make sure Docker Desktop is running.
2.  Open a terminal in the project's root directory.
3.  Run the following command:
    ```bash
    docker-compose up --build
    ```
4.  Wait for both services (`chatbot-1` and `mcp-server-1`) to build and start.
5.  Open your web browser and navigate to:
    **`http://localhost:8080`**

---

## Deployment
This application is configured for easy deployment to **Google Cloud Run**. The `cloudbuild.yaml` file and the `gcloud` deployment scripts used in our development can be adapted for a production CI/CD pipeline.
```eof
