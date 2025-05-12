class ApiUrls {
    constructor() {
        this.baseUrl = 'http://localhost:3000/api';
    }

    getVideos(filter = '') {
        return filter
            ? `${this.baseUrl}/videos?category=${encodeURIComponent(filter)}`
            : `${this.baseUrl}/videos`;
    }

    getVideoById(id) {
        return `${this.baseUrl}/videos/${id}`;
    }

    createVideo() {
        return `${this.baseUrl}/videos`;
    }

    updateVideoById(id) {
        return `${this.baseUrl}/videos/${id}`;
    }

    deleteVideoById(id) {
        return `${this.baseUrl}/videos/${id}`;
    }
}

export const apiUrls = new ApiUrls();