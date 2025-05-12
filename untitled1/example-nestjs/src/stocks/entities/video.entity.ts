import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm';

@Entity({ name: 'videos' })
export class Video {
    @PrimaryGeneratedColumn()
    id: number;

    @Column()
    title: string;

    @Column({ type: 'text', nullable: true })
    description: string;

    @Column()
    category: string;

    @Column({ name: 'preview_image', nullable: true })
    previewImage: string;

    @Column({ name: 'video_url' })
    videoUrl: string;

    @Column({ default: 0 })
    views: number;

    @Column({ default: 0 })
    likes: number;

    @Column({ name: 'upload_date', type: 'date' })
    uploadDate: string;
}