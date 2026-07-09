# Using a lightweight official Python 
FROM python
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 3000
# Run the application when the container starts
CMD ["python","app.py"]

