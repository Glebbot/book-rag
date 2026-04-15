FROM node:20-slim AS build
WORKDIR /app

COPY package*.json ./


RUN npm ci --include=optional

COPY . .

RUN npm run build

FROM nginx:stable-alpine
COPY nginx.conf.template /etc/nginx/templates/nginx.conf.template
COPY entrypoint.sh /entrypoint.sh
COPY --from=build /app/dist /usr/share/nginx/html

RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]