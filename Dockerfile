FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt /app/ 
RUN pip install -r requirements.txt 
COPY src/ /app/src/
EXPOSE 8000
CMD ["uvicorn", "src.main:main", "--host", "0.0.0.0", "--port", "8000"]
