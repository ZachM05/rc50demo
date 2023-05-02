FROM node:16-alpine

WORKDIR /app

COPY ["package.json", "yarn.lock", "./"]

ENV NEXT_PUBLIC_DATABASE_HOST mongodb

# RUN yarn install --proxy http://proxy.henkelgroup.net:80
RUN yarn install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]