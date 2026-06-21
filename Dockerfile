# Fase 3 — API Oficina: build multi-stage, runtime enxuto, usuário non-root.
# --- builder: compila dependências nativas e instala o pacote ---
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml requirements.txt ./
COPY app ./app

RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir --prefix=/install -e .

# --- runtime: imagem enxuta, sem toolchain, usuário não-root ---
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PATH="/install/bin:$PATH" \
    PYTHONPATH="/install/lib/python3.12/site-packages" \
    RUN_MIGRATIONS=false

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --create-home --shell /usr/sbin/nologin appuser

WORKDIR /app

COPY --from=builder /install /install
COPY alembic.ini alembic ./
COPY app ./app
COPY scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x /usr/local/bin/docker-entrypoint.sh \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
