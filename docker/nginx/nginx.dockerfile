FROM nginx:1.25.0-bullseye

RUN rm /etc/nginx/conf.d/default.conf
COPY rssreader.conf /etc/nginx/nginx.conf
RUN mkdir -p /app/static
