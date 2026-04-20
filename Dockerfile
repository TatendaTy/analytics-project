FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

# Install Python dependencies first for better layer caching.
COPY streamlit/requirements.txt /app/streamlit/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /app/streamlit/requirements.txt

# Copy Streamlit app source.
COPY streamlit /app/streamlit

EXPOSE 8000

WORKDIR /app/streamlit

CMD ["sh", "-c", "streamlit run streamlit_football_app.py --server.address 0.0.0.0 --server.port ${PORT}"]
