FROM node:alpine
WORKDIR /usr/src/app

ARG GEOSERVER_HOST
ARG GATEWAY_HOST
ENV GEOSERVER_HOST $GEOSERVER_HOST
ENV GATEWAY_HOST $GATEWAY_HOST

COPY . .
RUN chmod 755 createEnvFile.sh && ./createEnvFile.sh
RUN yarn install
RUN yarn global add serve

RUN yarn build
ENV PORT=1234
EXPOSE 1234
CMD ["serve", "dist"]
