FROM python:3.11-slim

RUN apt-get update && apt-get install -y graphviz

RUN pip install uv

WORKDIR /app

COPY pyproject.toml ./
RUN uv pip install --system -e .

COPY ./src ./src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]