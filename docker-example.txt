FROM ghcr.io/astral-sh/uv:python3.13-alpine

WORKDIR /app
COPY . .



RUN pip install uv

RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PORT=5000

EXPOSE 5000
CMD ["python", "src/python_service_template/app.py"]
