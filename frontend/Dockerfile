# build-stage for the frontend
# obsolute node
FROM node:12.6-alpine as build-stage
RUN apk update && \
    apk add git && \
    apk add --no-cache curl && \
    curl -o- -L https://yarnpkg.com/install.sh | sh
ENV PATH $HOME/.yarn/bin:$HOME/.config/yarn/global/node_modules/.bin:$PATH

WORKDIR /app
COPY package*.json /app
RUN yarn install && yarn nbp

# ARG FRONTEND_ENV=development
# ARG FRONTEND_ENV=production
# ENV VUE_APP_ENV=${FRONTEND_ENV}
COPY ./ /app
RUN yarn sta-build


# production-stage
FROM nginx:stable-alpine as production-stage
COPY ./nginx/ /etc/nginx
COPY --from=build-stage /app/dist/ /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;","-c","/etc/nginx/nginx.conf"]
