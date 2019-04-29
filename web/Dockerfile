# building web application
FROM node:10.15-alpine
WORKDIR /usr/src/app

ARG GATEWAY_HOST
ENV GATEWAY_HOST $GATEWAY_HOST

COPY createEnvFile.sh ./
RUN chmod 755 createEnvFile.sh && ./createEnvFile.sh

COPY package.json ./
COPY yarn.lock ./

RUN yarn install --production --pure-lockfile

COPY src ./src

RUN yarn build


# deploying web application
FROM nginx:stable-alpine

COPY --from=0 /usr/src/app/dist /usr/share/nginx/html/

CMD ["nginx", "-g", "daemon off;"]
