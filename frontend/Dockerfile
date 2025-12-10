# frontend/Dockerfile

# Простой dev-образ для Next.js приложения

FROM node:20-alpine

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем package.json и package-lock.json
COPY frontend/package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем исходный код фронтенда
COPY frontend/ ./

# Открываем порт, на котором будет работать Next.js
EXPOSE 3000

# Запуск в dev-режиме (подходит для MVP и отладки)
CMD ["npm", "run", "dev"]
