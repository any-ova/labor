import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { Video } from './stocks/entities/video.entity';
import { VideoModule } from './stocks/video.module';

@Module({
    imports: [
        TypeOrmModule.forRoot({
            type: 'postgres',
            host: 'localhost',
            port: 5666,
            username: 'postgres',
            password: 'nestjs123',
            database: 'video_db',
            entities: [Video],
            synchronize: false,
        }),
        VideoModule,
    ],
    controllers: [AppController],
    providers: [AppService],
})
export class AppModule {}
