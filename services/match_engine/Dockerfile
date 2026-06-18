FROM node:25-alpine

WORKDIR /app

# Install Bun globally inside the Alpine image as requested
RUN npm install -g bun

COPY package.json .
RUN bun install

# Create the data directory for the SQLite volume
RUN mkdir -p /app/data

COPY . .

EXPOSE 8002

# Run the engine using Bun
CMD ["bun", "run", "src/index.js"]