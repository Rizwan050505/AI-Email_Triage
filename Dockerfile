FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install openai pydantic pydantic-settings

# Hugging Face permissions requirement
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

COPY --chown=user . .

RUN python backend/training/train_classifier.py
RUN python chatbot/train.py

EXPOSE 7860

# Run the FastAPI server to keep the Space alive, evaluators will still test inference.py externally.
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
