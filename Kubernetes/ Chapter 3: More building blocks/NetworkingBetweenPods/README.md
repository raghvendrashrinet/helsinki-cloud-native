### Networkin Between Pods

- A debugging pod
  You can just go inside a pod or send a request manually from another pod,You can use eg. busybox  a light weight Linux distro for debugging.
  ```
   $ kubectl exec -it my-busybox -- wget -qO - http://todo-backend-svc:2345  
     # 2345 is svc port , target port will of pod and endpoint will have pod IP's

   ### Or Open shell and fire cmd inside it
   $ kubectl exec -it my-busybox -- sh
    # wget -qO - http://todo-backend-svc:2345

  ### or access pod on listening port directly
   $ kubectl exec -it my-busybox wget -qO - http://10.42.0.63:3000
  ```
  Or You can get same result using svc cluster ip 
  ```
   $ kubectl exec -it my-busybox -- wget -qO - http://10.43.89.182:2345
  ```
   
