import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { CreateVideoDto } from './dto/create-video.dto';
import { UpdateVideoDto } from './dto/update-video.dto';
import { Video } from './entities/video.entity';

@Injectable()
export class VideoService {
    constructor(
        @InjectRepository(Video)
        private videoRepository: Repository<Video>,
    ) {}

    async create(createVideoDto: CreateVideoDto): Promise<Video> {
        const newVideo = this.videoRepository.create({
            ...createVideoDto,
            views: 0,
            likes: 0,
            uploadDate: new Date().toISOString().split('T')[0],
        });
        return await this.videoRepository.save(newVideo);
    }

    async findAll(category?: string): Promise<Video[]> {
        if (category) {
            return this.videoRepository
                .createQueryBuilder('video')
                .where('LOWER(video.category) LIKE LOWER(:category)', {
                    category: `%${category}%`
                })
                .getMany();
        }
        return this.videoRepository.find();
    }

    async findOne(id: number): Promise<Video | null> {
        return await this.videoRepository.findOne({ where: { id } });
    }

    async update(id: number, updateVideoDto: UpdateVideoDto): Promise<Video | null> {
        await this.videoRepository.update(id, updateVideoDto);
        return this.findOne(id);
    }

    async remove(id: number): Promise<boolean> {
        const result = await this.videoRepository.delete(id);
        return (result.affected || 0) > 0;
    }
}