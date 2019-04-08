FROM node:alpine
WORKDIR /usr/src/app

ARG GATEWAY_HOST
ENV GATEWAY_HOST $GATEWAY_HOST

COPY createEnvFile.sh ./
RUN chmod 755 createEnvFile.sh && ./createEnvFile.sh

COPY package.json ./
COPY yarn.lock ./

RUN yarn install --production --pure-lockfile

COPY src ./src

RUN yarn global add serve

RUN yarn build
ENV PORT=1234
EXPOSE 1234
CMD ["serve", "dist"]
