import { Carousel } from '../../components/carousel/index.js';

export function renderArtPage() {
    const artImages = [
        { image: 'img/art1.jpg', alt: 'Картина 1' },
        { image: 'img/art2.jpg', alt: 'Картина 2' },
        { image: 'img/art3.jpg', alt: 'Картина 3' }
    ];

    document.getElementById('app').innerHTML = `
        <div class="container">
            <h2 class="text-primary">Искусство</h2>
            ${Carousel(artImages)}
            <button class="btn btn-secondary mt-3" onclick="renderMainPage()">Назад на главную</button>
        </div>
    `;
}
