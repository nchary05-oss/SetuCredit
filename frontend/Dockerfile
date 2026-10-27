FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
# nginx templating: /etc/nginx/templates/*.template is envsubst-ed into
# /etc/nginx/conf.d/. BACKEND_URL = nginx's proxy target (compose default);
# PWA_API_BASE = browser-side API base baked into config.js (empty locally,
# the backend's public URL on Render — avoids nginx-to-nginx proxying).
ENV BACKEND_URL=http://backend:8000 \
    PWA_API_BASE=
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY config.js.template /usr/share/nginx/html/config.js.template
COPY --chmod=755 40-setucredit-config.sh /docker-entrypoint.d/40-setucredit-config.sh
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
