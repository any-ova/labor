import { Repository } from 'typeorm';
import { CreateVideoDto } from './dto/create-video.dto';
import { UpdateVideoDto } from './dto/update-video.dto';
import { Video } from './entities/video.entity';
export declare class VideoService {
    private videoRepository;
    constructor(videoRepository: Repository<Video>);
    create(createVideoDto: CreateVideoDto): Promise<Video>;
    findAll(category?: string): Promise<Video[]>;
    findOne(id: number): Promise<Video | null>;
    update(id: number, updateVideoDto: UpdateVideoDto): Promise<Video | null>;
    remove(id: number): Promise<boolean>;
}
