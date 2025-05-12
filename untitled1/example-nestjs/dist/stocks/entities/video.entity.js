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
Object.defineProperty(exports, "__esModule", { value: true });
exports.Video = void 0;
const typeorm_1 = require("typeorm");
let Video = class Video {
    id;
    title;
    description;
    category;
    previewImage;
    videoUrl;
    views;
    likes;
    uploadDate;
};
exports.Video = Video;
__decorate([
    (0, typeorm_1.PrimaryGeneratedColumn)(),
    __metadata("design:type", Number)
], Video.prototype, "id", void 0);
__decorate([
    (0, typeorm_1.Column)(),
    __metadata("design:type", String)
], Video.prototype, "title", void 0);
__decorate([
    (0, typeorm_1.Column)({ type: 'text', nullable: true }),
    __metadata("design:type", String)
], Video.prototype, "description", void 0);
__decorate([
    (0, typeorm_1.Column)(),
    __metadata("design:type", String)
], Video.prototype, "category", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'preview_image', nullable: true }),
    __metadata("design:type", String)
], Video.prototype, "previewImage", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'video_url' }),
    __metadata("design:type", String)
], Video.prototype, "videoUrl", void 0);
__decorate([
    (0, typeorm_1.Column)({ default: 0 }),
    __metadata("design:type", Number)
], Video.prototype, "views", void 0);
__decorate([
    (0, typeorm_1.Column)({ default: 0 }),
    __metadata("design:type", Number)
], Video.prototype, "likes", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'upload_date', type: 'date' }),
    __metadata("design:type", String)
], Video.prototype, "uploadDate", void 0);
exports.Video = Video = __decorate([
    (0, typeorm_1.Entity)({ name: 'videos' })
], Video);
//# sourceMappingURL=video.entity.js.map