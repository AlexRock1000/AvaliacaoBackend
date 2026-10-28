# etapa 1: uma imagem com Node só para gerar o build
FROM node:22 AS build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# etapa 2: o Caddy, levando o build da etapa 1 e a configuração da aula
FROM caddy:2
COPY --from=build /app/dist /srv
COPY Caddyfile /etc/caddy/Caddyfile
