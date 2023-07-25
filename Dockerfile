FROM python:3.7.16
COPY main.py models.py requirements.txt /app/
RUN pip install -r /app/requirements.txt
WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]