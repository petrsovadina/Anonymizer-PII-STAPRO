# Multi-stage build pro optimalizovaný Docker image
FROM python:3.11-slim as builder

# Nastavení pracovního adresáře
WORKDIR /app

# Kopírování requirements.txt pro lepší cache využití
COPY requirements.txt .

# Vytvoření virtual environment a instalace závislostí
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Aktualizace pip a instalace závislostí
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stažení spaCy modelu
RUN python -m spacy download cs_core_news_sm

# Production stage
FROM python:3.11-slim

# Instalace systémových závislostí pro health check
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Nastavení pracovního adresáře
WORKDIR /app

# Kopírování virtual environment z builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Vytvoření neprivilegovaného uživatele
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app

# Kopírování aplikačních souborů
COPY --chown=app:app . .

# Vytvoření potřebných adresářů
RUN mkdir -p uploads exports logs data && \
    chown -R app:app uploads exports logs data

# Přepnutí na neprivilegovaného uživatele
USER app

# Exponování portu
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Spuštění aplikace
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
