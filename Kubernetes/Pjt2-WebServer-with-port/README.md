Build Image 
 > docker build -t raghvendrashrinet/test:a1 .
Push to Docker Hub , kubernetes searches docker hub for the image
> docker push

Run Container
>  kubectl run --image=raghvendrashrinet/test:a1 webapp

Port Fort local host to pod port
> kubectl port-forward pod/web-app 3000:3000

for deplyment port forwarding
> kubectl port-forward deployment/web-server 3000:3005 

Browse 
`http://localhost:3000/`


## Run the Pod with a Specific Port
First, create the pod and set the PORT environment variable via CLI:  
`kubectl run my-app --image=<your-image> --env="PORT=3005" --port=3005   `  

- --env="PORT=3005": Tells your app to listen on 3005.
- --port=3005: Documents that the container exposes this port. 

---
In docker to provide specific port
```bash
docker run -e PORT=3005 -p 3005:3005 <your-image>
```


