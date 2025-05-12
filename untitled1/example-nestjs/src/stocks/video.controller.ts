import { Controller, Get, Post, Body, Patch, Param, Delete, Query } from '@nestjs/common';
import { VideoService } from './video.service';
import { CreateVideoDto } from './dto/create-video.dto';
import { UpdateVideoDto } from './dto/update-video.dto';

@Controller('videos')
export class VideoController {
  constructor(private readonly videoService: VideoService) {}

  @Post()
  async create(@Body() createVideoDto: CreateVideoDto) {
    console.log('Получены данные:', createVideoDto); // Добавьте эту строку
    return this.videoService.create(createVideoDto);
  }

  @Get()
  async findAll(@Query('category') category?: string) {
    return this.videoService.findAll(category);
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    return this.videoService.findOne(+id);
  }

  @Patch(':id')
  async update(@Param('id') id: string, @Body() updateVideoDto: UpdateVideoDto) {
    return this.videoService.update(+id, updateVideoDto);
  }

  @Delete(':id')
  async remove(@Param('id') id: string) {
    return this.videoService.remove(+id);
  }
}