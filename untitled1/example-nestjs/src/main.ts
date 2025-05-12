import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { NestExpressApplication } from '@nestjs/platform-express';
import { join } from 'path';

async function bootstrap() {
  // 1. Создаем приложение с поддержкой Express
  const app = await NestFactory.create<NestExpressApplication>(AppModule);

  // 2. Настройка CORS для фронтенда
  app.enableCors({
    origin: [
      'http://localhost:5500', // Live Server
      'http://127.0.0.1:5500', // Альтернативный адрес
      'http://localhost:3000', // NestJS
      'http://localhost:63342' // WebStorm
    ],
    methods: 'GET,HEAD,PUT,PATCH,POST,DELETE',
    credentials: true,
    allowedHeaders: 'Content-Type,Authorization'
  });

  // 3. Обслуживание статических файлов фронтенда
  app.useStaticAssets(join(__dirname, '..', 'public'));

// main.ts
  app.useStaticAssets(join(__dirname, '..', 'public'), {
    prefix: '/',
    fallthrough: true // Позволяет продолжить обработку если файл не найден
  });
  // 4. Глобальный префикс для API
  app.setGlobalPrefix('api');

  // 5. Запуск сервера
  const port = process.env.APP_PORT || 3000;
  await app.listen(port);
  console.log(`Application is running on: http://localhost:${port}`);
}

bootstrap();