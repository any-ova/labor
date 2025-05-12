import { ajax } from './modules/ajax.js';
import { apiUrls } from './modules/urls.js';

class VideoPage {
    constructor() {
        // Проверка обязательных элементов
        this.requiredElements = [
            'mainVideo', 'videoTitle', 'videoDescription', 'videoCategory',
            'videoViews', 'videoLikes', 'videoDate', 'editForm',
            'editTitle', 'editDescription', 'editCategory',
            'editBtn', 'saveBtn', 'cancelBtn', 'deleteBtn', 'message'
        ];

        this.elements = {};
        this.init();
    }

    init() {
        // Инициализация элементов с проверкой
        this.requiredElements.forEach(id => {
            this.elements[id] = document.getElementById(id);
            if (!this.elements[id]) {
                console.error(`Элемент #${id} не найден!`);
            }
        });

        // Проверка ID видео в URL
        const urlParams = new URLSearchParams(window.location.search);
        this.videoId = urlParams.get('id');

        if (!this.videoId) {
            this.showMessage('Видео не найдено', 'error');
            setTimeout(() => window.location.href = 'index.html', 2000);
            return;
        }

        this.setupEventListeners();
        this.loadVideo();
    }

    async loadVideo() {
        try {
            const video = await ajax.get(apiUrls.getVideoById(this.videoId));
            if (!video) throw new Error('Видео не найдено');

            this.currentVideo = video;
            this.safeRenderVideo(video);
        } catch (error) {
            console.error('Ошибка загрузки:', error);
            this.showMessage('Не удалось загрузить видео', 'error');
        }
    }

    safeRenderVideo(video) {
        // Безопасный рендеринг с проверкой элементов
        const safeSet = (id, value) => {
            if (this.elements[id]) {
                this.elements[id].textContent = value || '';
            }
        };

        try {
            if (this.elements.mainVideo) {
                this.elements.mainVideo.src = video.videoUrl || '';
            }

            safeSet('videoTitle', video.title);
            safeSet('videoDescription', video.description);
            safeSet('videoCategory', `Категория: ${video.category}`);
            safeSet('videoViews', `${this.formatNumber(video.views)} просмотров`);
            safeSet('videoLikes', `${this.formatNumber(video.likes)} лайков`);
            safeSet('videoDate', `Опубликовано: ${video.uploadDate}`);
        } catch (error) {
            console.error('Ошибка рендеринга:', error);
        }
    }

    setupEventListeners() {
        // Безопасная привязка событий
        if (this.elements.editBtn) {
            this.elements.editBtn.addEventListener('click', () => this.toggleEditForm(true));
        }

        if (this.elements.saveBtn) {
            this.elements.saveBtn.addEventListener('click', (e) => this.handleSave(e));
        }



        const { editBtn, saveBtn, cancelBtn, deleteBtn } = this.elements;

        editBtn.addEventListener('click', () => this.toggleEditForm(true));
        cancelBtn.addEventListener('click', () => this.toggleEditForm(false));
        saveBtn.addEventListener('click', (e) => this.handleSave(e));
        deleteBtn.addEventListener('click', () => this.deleteVideo());
    }

    toggleEditForm(show) {
        const { editForm, editTitle, editDescription, editCategory } = this.elements;

        if (show) {
            editTitle.value = this.currentVideo.title;
            editDescription.value = this.currentVideo.description;
            editCategory.value = this.currentVideo.category;
            editForm.style.display = 'block';
        } else {
            editForm.style.display = 'none';
        }
    }

    async handleSave(e) {
        e.preventDefault();

        try {
            const updatedData = {
                title: this.elements.editTitle.value,
                description: this.elements.editDescription.value,
                category: this.elements.editCategory.value
            };

            const updatedVideo = await ajax.patch(
                apiUrls.updateVideoById(this.videoId),
                updatedData
            );

            this.currentVideo = updatedVideo;
            this.renderVideo(updatedVideo);
            this.toggleEditForm(false);
            this.showMessage('Изменения сохранены!', 'success');
        } catch (error) {
            console.error('Ошибка сохранения:', error);
            this.showMessage('Ошибка при сохранении', 'error');
        }
    }

    async deleteVideo() {
        if (!confirm('Удалить это видео?')) return;

        try {
            await ajax.delete(apiUrls.deleteVideoById(this.videoId));
            this.showMessage('Видео удалено!', 'success');
            setTimeout(() => window.location.href = 'index.html', 1500);
        } catch (error) {
            console.error('Ошибка удаления:', error);
            this.showMessage('Ошибка при удалении', 'error');
        }
    }

    showMessage(text, type) {
        const { messageDiv } = this.elements;
        messageDiv.textContent = text;
        messageDiv.className = `message ${type}`;
        setTimeout(() => messageDiv.textContent = '', 3000);
    }

    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new VideoPage();
});