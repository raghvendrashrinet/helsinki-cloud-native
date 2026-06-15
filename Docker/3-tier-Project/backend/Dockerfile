FROM golang:1.16
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
## ex1.14 env adding for cors
ENV REQUEST_ORIGIN=http://localhost:5001  
COPY . ./
RUN CGO_ENABLED=0 GOOS=linux go build
EXPOSE 8080
# Run
CMD ["./server"]
