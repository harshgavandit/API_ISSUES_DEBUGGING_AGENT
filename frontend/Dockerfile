# API Reliability Copilot — frontend image
FROM node:22-alpine

WORKDIR /app

ARG NEXT_PUBLIC_API_BASE=http://localhost:8000
ENV NEXT_PUBLIC_API_BASE=${NEXT_PUBLIC_API_BASE}

COPY package*.json ./
RUN npm ci

COPY . .
ENV NODE_ENV=production
RUN npm run build

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD sh -c "wget -qO- http://127.0.0.1:3000 >/dev/null 2>&1 || exit 1"

CMD ["npm", "run", "start", "--", "-H", "0.0.0.0"]
