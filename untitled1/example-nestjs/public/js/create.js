import { ajax } from './modules/ajax.js';
import { apiUrls } from './modules/urls.js';

class CreateVideoPage {
    constructor() {
        this.videoForm = document.getElementById('videoForm');
        this.messageEl = document.getElementById('message');

        this.initEvents();
    }

    initEvents() {
        this.videoForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.createVideo();
        });
    }

    createVideo() {
        const videoData = {
            title: document.getElementById('title').value,
            description: document.getElementById('description').value,
            category: document.getElementById('category').value,
            previewImage: document.getElementById('previewImage').value,
            videoUrl: document.getElementById('videoUrl').value,
            views: 0,
            likes: 0,
            uploadDate: new Date().toISOString().split('T')[0]
        };

        ajax.post(apiUrls.createVideo(), videoData, (data, status) => {
            if (status === 201) {
                this.showMessage('Видео успешно опубликовано!', 'success');
                setTimeout(() => {
                    window.location.href = '/index.html';
                }, 1500);
            } else {
                this.showMessage('Ошибка при публикации видео', 'error');
            }
        });
    }

    showMessage(text, type) {
        this.messageEl.textContent = text;
        this.messageEl.className = `message ${type}`;
    }
}

new CreateVideoPage();