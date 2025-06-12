FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y gcc libpq-dev
RUN rm -rf .venv
RUN pip install uv
RUN uv sync

EXPOSE 8000

CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]