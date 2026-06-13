
### Commands notes
**stop and removing container 
```
> docker container stop <id name> 
> docker container rm < id name>
```
OR in online use force
```
> docker rm --force <id name> 
```
Image remove
> docker image rm < image name >

Logs view
> docker logs -f looper

Pausing and attaching container
```
docker pause <> 
docker unpause <>
docker attach <>  --> gets std in and std out--> exit kills container
docker attach --no-stdin <>  --> gets only stdout
```

killing container
```
docker kill looper && docker rm looper
  -- or similer effect   docker rm --force looper
```

'rm' in docker run ensure container get removed after finish 
```
  docker run -d --rm -it --name looper-it ubuntu sh -c 'while true; do date; sleep 1; done'
```
   
  ##### Note : attach to the container and hit control+p, control+q to detach us from the STDOUT.
