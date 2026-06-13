## ENTRYPOINT and CMD arguments

- #### Use CMD for default, which you to override if required by paasing argument at creation
- #### Entrypoint can't be overriden by passing argument,argument gets appended

argument can be defined two way
> exec form and shell form

- exec form is generally preferred over the shell form, because in the shell form the command that is executed is wrapped with /bin/sh -c, which can result in unexpected behaviour.
- the shell form can be useful in certain situations, for example, when you need to evaluate environment variables in the command like $MYSQL_PASSWORD or similar.

#### shell form, the command is provided as a string without brackets, see how they interpreted in different ways how gets prefxed by /bin/sh -c

| Dockerfile | Resulting command |
| :--- | :--- |
| `ENTRYPOINT /bin/ping -c 3`<br>`CMD localhost` | `/bin/sh -c '/bin/ping -c 3'` `/bin/sh -c localhost` |
| `ENTRYPOINT ["/bin/ping","-c","3"]`<br>`CMD localhost` | `/bin/ping -c 3` `/bin/sh -c localhost` |
| `ENTRYPOINT /bin/ping -c 3`<br>`CMD ["localhost"]` | `/bin/sh -c '/bin/ping -c 3'` `localhost` |
| `ENTRYPOINT ["/bin/ping","-c","3"]`<br>`CMD ["localhost"]` | `/bin/ping -c 3` `localhost` |

---
##### Example 1 images
- Python : default to help with CMD
  to override help ,    pass argument eg --version
```
FROM python:3.11
ENTRYPOINT ["python3"]
CMD ["--help"]
```
##### Example 2 , execute script
script.sh
```
#!/bin/bash

echo "Searching..";
sleep 1;
curl http://$1;
```
Dockerfile
```
FROM ubuntu:24.04
RUN apt update -y && apt install -y curl
RUN mkdir /script
WORKDIR /script
COPY script.sh .
RUN chmod +x script.sh
ENTRYPOINT ["./script.sh"]
```
Now build and run
```
$ docker build -t curler-v2 .
$ docker run curler-v2 helsinki.fi
```
$1: is the first command-line argument passed to the script
