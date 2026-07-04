

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
COPY *.py .
CMD ["python","app.py"]
```

---

### For this various steps to consider 
#### step 1 : To mount logs to a host location, Which will be letter picked by display container
##### some tips to use path in docker
1. Use an absolute path or the $PWD variable to ensure Docker finds the correct file.
 - Instead of ../log.txt, use: -   ` -v $PWD/../log.txt:/app/log.txt ` or use ` full absolute path`

2 Create the file explicitly on the host:(log.txt in logs folder)
  - Ensure the parent folder exists: `mkdir -p $PWD/../logs`
  - Create the actual file,as it should prexist before container start
  ##### Because your Python script opens log.txt in append mode ("a"), the file must exist as a regular file on the host before you start the container.If the file is missing, Docker interprets the mount path as a request for a directory and creates a folder named log.txt instead. When your script tries to write to this "file," it crashes with IsADirectoryError because it is actually a folder

If the file is missing, Docker interprets the mount path as a request for a directory and creates a folder named log.txt instead. When your script tries to write to this "file," it crashes with IsADirectoryError because it is actually a folder.
3 Run Contaile
```
  docker run -v $PWD/../logs/log.txt:/app/log.txt -d -p 5000:5000 --name ab raghvendrashrinet/projects:hashgenv1
```

All commands 
```
# 1. Ensure the parent directory exists
mkdir -p $PWD/../logs

# 2. Create the empty log file (CRITICAL STEP)
# This ensures it is a file, not a directory
touch $PWD/../logs/log.txt

# 3. Verify it is a file (should show '-rw-r--r--', not 'd')
ls -l $PWD/../logs/log.txt

# 4. Now start the container
docker run -v $PWD/../logs/log.txt:/app/log.txt -d -p 5000:5000 --name ab raghvendrashrinet/projects:hashgenv1
```

### Now second container, This app will read log file and display on browser

1. Build image
   ```
    docker build -t raghvendrashrinet/projects:webappv1 .
   ```
2. Application is listening on port 8000, So we will map port 8000
   ```
     # volume same log file mounted on /app/log.txt
     # host port 8000 is exposed
     docker run -v $PWD/../logs/log.txt:/app/log.txt -d -p 8000:8000 --name ab raghvendrashrinet/projects:webappv1
   
    ```
3. Browse `http://localhost:8000/`
   
