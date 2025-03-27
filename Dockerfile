FROM python:3.10-slim

RUN pip install poetry

# Install the required dependencies for running Playwright browsers
RUN apt-get update && \
    apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libnss3-tools \
    libgdk-pixbuf2.0-0 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libdbus-1-3 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libnspr4 \
    libexpat1 \
    libxfixes3 \
    libxext6 \
    libxkbcommon0 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app

COPY . .

RUN poetry install

RUN poetry run playwright install chromium

CMD ["poetry", "run", "python", "src/technesis/main.py"]