"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var __param = (this && this.__param) || function (paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.VideoService = void 0;
const common_1 = require("@nestjs/common");
const typeorm_1 = require("@nestjs/typeorm");
const typeorm_2 = require("typeorm");
const video_entity_1 = require("./entities/video.entity");
let VideoService = class VideoService {
    videoRepository;
    constructor(videoRepository) {
        this.videoRepository = videoRepository;
    }
    async create(createVideoDto) {
        const newVideo = this.videoRepository.create({
            ...createVideoDto,
            views: 0,
            likes: 0,
            uploadDate: new Date().toISOString().split('T')[0],
        });
        return await this.videoRepository.save(newVideo);
    }
    async findAll(category) {
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
    async findOne(id) {
        return await this.videoRepository.findOne({ where: { id } });
    }
    async update(id, updateVideoDto) {
        await this.videoRepository.update(id, updateVideoDto);
        return this.findOne(id);
    }
    async remove(id) {
        const result = await this.videoRepository.delete(id);
        return (result.affected || 0) > 0;
    }
};
exports.VideoService = VideoService;
exports.VideoService = VideoService = __decorate([
    (0, common_1.Injectable)(),
    __param(0, (0, typeorm_1.InjectRepository)(video_entity_1.Video)),
    __metadata("design:paramtypes", [typeorm_2.Repository])
], VideoService);
//# sourceMappingURL=video.service.js.map