# Nginx Dockerfile
FROM nginx:1.25-alpine

# 기본 설정 제거 및 커스텀 설정 복사
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/

EXPOSE 80
