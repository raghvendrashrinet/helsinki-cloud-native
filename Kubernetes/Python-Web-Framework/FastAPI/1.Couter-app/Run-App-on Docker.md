## Build 
 ```
 docker build -t raghvendrashrinet/projects:1.8 .
```
## Docker run , bind host port to container port 8000 , to browse on host pc
```
docker run  -p 8000:8000 raghvendrashrinet/projects:1.8
```

### Browse 
```
http://localhost:8000
``` 
