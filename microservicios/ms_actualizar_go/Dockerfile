FROM golang:1.22-alpine AS build
WORKDIR /app
COPY go.mod ./
COPY main.go openapi.json ./
RUN go mod tidy && CGO_ENABLED=0 go build -o /servicio .

FROM alpine:3.20
RUN apk add --no-cache ca-certificates
COPY --from=build /servicio /servicio
ENV PORT=8000
EXPOSE 8000
CMD ["/servicio"]
