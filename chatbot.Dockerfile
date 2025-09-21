FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y portaudio19-dev && rm -rf /var/lib/apt/lists/*
COPY chatbot.requirements.txt .
RUN pip install --no-cache-dir -r chatbot.requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "emoAI.py"]