## Project : material-applications /spring-example-project/
README.md
```
Simple button
How to start
Make sure you have java 8 installed

Build the project with ./mvnw package

Run with java -jar ./target/docker-example-1.1.3.jar

The project should open in 8080 and you get a message by pressing the button.
```
---
Dockerfile 
```Dockerfile
FROM amazoncorretto:8
WORKDIR /mydir
EXPOSE 8080
COPY . .
RUN ./mvnw package
ENTRYPOINT ["java","-jar","./target/docker-example-1.1.3.jar"]
```
Build and Run
```bash
> docker build -t spring .
> docker run -p 8080:8080 spring
```
