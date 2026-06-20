Build Image 
 > docker build -t raghvendrashrinet/test:a1 .
Push to Docker Hub , kubernetes searches docker hub for the image
> docker push

Run Container
>  kubectl run --image=raghvendrashrinet/test:a1 todo-app # takes default port 3000 if no port specified

Port Fort local host to pod port
> kubectl port-forward pod/todo-app 3000:3000

for deplyment port forwarding
 `kubectl port-forward deployment/web-server 3000:3005`  <local port(host)>:<container port>

Browse 
`http://localhost:3000/`


## Run the Pod with a Specific Port
First, create the pod and set the PORT environment variable via CLI:  
`kubectl run my-app --image=<your-image> --env="PORT=3005" --port=3005`
or you can drop `--port=3005`,--port flag simply populates the containerPort field in the Pod's configuration file (spec.containers[0].ports). This field is purely metadata (documentation).  
Even without explicitly declaring --port=3005, the port is still open internally.  

so this also works same : `kubectl run my-app --image=<your-image> --env="PORT=3005"`
- --env="PORT=3005": Tells your app to listen on 3005.
- --port=3005: Documents that the container exposes this port. 

---
In docker to provide specific port
```bash
docker run -e PORT=3005 -p 3005:3005 <your-image>
```


