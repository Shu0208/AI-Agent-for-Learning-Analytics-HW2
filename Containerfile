FROM docker.io/library/python:3.12-slim
WORKDIR /opt/grader
COPY app/agent.py app/worker.py ./
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
CMD ["python", "-I", "-B", "/opt/grader/agent.py"]
