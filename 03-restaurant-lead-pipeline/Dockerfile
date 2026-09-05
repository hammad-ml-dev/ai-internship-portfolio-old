FROM python:3.11-slim

WORKDIR /app

COPY web_app/requirements-deploy.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY web_app/ /app/

ENV PORT=5000
EXPOSE 5000

CMD ["sh", "-c", "gunicorn working_app:app --bind 0.0.0.0:${PORT} --workers 1 --threads 4 --timeout 120"]
