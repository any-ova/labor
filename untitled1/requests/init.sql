CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    preview_image VARCHAR(255),
    video_url VARCHAR(255) NOT NULL,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    upload_date DATE DEFAULT CURRENT_DATE
);

INSERT INTO videos (title, description, category, preview_image, video_url, views, likes)
VALUES
    ('Introduction to NestJS', 'Learn NestJS basics', 'Programming', 'nestjs.jpg', 'https://example.com/nestjs', 100, 25),
    ('Docker for Beginners', 'Docker fundamentals', 'DevOps', 'docker.jpg', 'https://example.com/docker', 150, 40)
ON CONFLICT (id) DO NOTHING;