import { ajax } from './modules/ajax.js';
import { apiUrls } from './modules/urls.js';

class VideoApp {
    constructor() {
        this.videosList = document.getElementById('videosList');
        this.filterInput = document.getElementById('filterInput');
        this.currentFilter = '';

        this.initEvents();
        this.loadVideos();
    }

    initEvents() {
        this.filterInput.addEventListener('input', (e) => {
            this.currentFilter = e.target.value;
            this.loadVideos();
        });
    }

    async loadVideos() {
        try {
            const videos = await ajax.get(apiUrls.getVideos(this.currentFilter));

            if (!videos || !Array.isArray(videos)) {
                throw new Error('Некорректный формат данных');
            }

            this.renderVideos(videos);
        } catch (error) {
            console.error('Ошибка загрузки:', error);
            this.videosList.innerHTML = `
            <div class="error-message">
                <p>Ошибка загрузки видео</p>
                <p>${error.message}</p>
            </div>
        `;
        }
    }

    renderVideos(videos) {
        this.videosList.innerHTML = videos.length
            ? videos.map(video => `
                <div class="video-card">
                    <img src="${video.previewImage}" alt="${video.title}">
                    <h3>${video.title}</h3>
                    <p class="category">${video.category}</p>
                    <p class="views">${this.formatViews(video.views)} просмотров</p>
                    <a href="video.html?id=${video.id}" class="btn">Смотреть</a>
                </div>
            `).join('')
            : '<p class="empty">Видео не найдены</p>';
    }

    formatViews(views) {
        return views.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new VideoApp();
});