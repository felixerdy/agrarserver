FROM node:alpine
WORKDIR /usr/src/app

COPY . .
RUN yarn install
RUN yarn global add serve
RUN yarn build
ENV PORT=1234
EXPOSE 1234
CMD ["serve", "dist"]