import { VideoService } from './video.service';
import { CreateVideoDto } from './dto/create-video.dto';
import { UpdateVideoDto } from './dto/update-video.dto';
export declare class VideoController {
    private readonly videoService;
    constructor(videoService: VideoService);
    create(createVideoDto: CreateVideoDto): Promise<import("./entities/video.entity").Video>;
    findAll(category?: string): Promise<import("./entities/video.entity").Video[]>;
    findOne(id: string): Promise<import("./entities/video.entity").Video | null>;
    update(id: string, updateVideoDto: UpdateVideoDto): Promise<import("./entities/video.entity").Video | null>;
    remove(id: string): Promise<boolean>;
}
