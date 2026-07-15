FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
COPY ca-bundle.crt* /root/.ccr/

RUN if [ -f /root/.ccr/ca-bundle.crt ]; then \
      npm config set cafile /root/.ccr/ca-bundle.crt; \
    fi && \
    npm install

COPY . .

ENV REACT_APP_API_URL=http://localhost:8000

CMD ["npm", "start"]
