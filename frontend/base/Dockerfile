FROM node:20-alpine

WORKDIR /app

# 复制基座 package.json
COPY base/package*.json /app/base/
WORKDIR /app/base
RUN npm install

COPY base/ /app/base/

EXPOSE 3000

CMD ["npm", "run", "dev"]
