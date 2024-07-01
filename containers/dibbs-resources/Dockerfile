FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci
COPY . .

# Expose the port the app runs on
EXPOSE 3000

# Run the application
CMD ["npm", "start"]
