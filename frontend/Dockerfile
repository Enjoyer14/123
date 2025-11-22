FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install
RUN npm install react-markdown@^9 remark-gfm@^4

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host"]
