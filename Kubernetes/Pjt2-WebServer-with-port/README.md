Build Image 
 > docker build -t raghvendrashrinet/test:a1 .
Push to Docker Hub , kubernetes searches docker hub for the image
> docker push

Run Container
>  kubectl run --image=raghvendrashrinet/test:a1 webapp

Port Fort local host to pod port
> kubectl port-forward pod/web-app 3000:3000

Browse 
`http://localhost:3000/`



