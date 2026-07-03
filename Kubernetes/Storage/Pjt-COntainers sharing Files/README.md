

## 1 Loggenerator app generate log
- generates log.txt file with hash value
## 2. web app will display the log from shared log
- displays log.txt on web
## Testing locallu
 - `python .\logoutput.py`
 - `python .\Webapp.py`
   ```
    
    INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
    INFO:     127.0.0.1:62345 - "GET / HTTP/1.1" 200 OK
    INFO:     127.0.0.1:62345 - "GET /stream HTTP/1.1" 200 OK

   ```
   
---
## Testing with docker on host machine
1. python env
   ` python -m venv myenv`
2. switch to env
   `.\myenv\Scripts\activate`
3. Install requirements
   pip install  fastapi uvicorn gunicorn sse_starlette
4. Build docker image
```dockerfile
FROM python
WORKDIR /app
COPY  requirements.txt .
RUN pip install -r requirements.txt
COPY *.py .
CMD ["python","app.py"]
```


   
