# etapa 1: uma imagem com Node só para gerar o build
FROM node:22 AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . ./
RUN npm run build

# etapa 2: o Caddy recebe só os arquivos gerados na etapa 1
FROM caddy:2
COPY --from=build /app/dist /srv
