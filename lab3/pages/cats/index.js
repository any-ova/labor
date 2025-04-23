import { Carousel } from '../../components/carousel/index.js';

export function renderCatsPage() {
    const catsGifs = [
        { image: 'img/cat1.gif', alt: 'Котик 1' },
        { image: 'img/cat2.gif', alt: 'Котик 2' },
        { image: 'img/cat3.gif', alt: 'Котик 3' }
    ];

    document.getElementById('app').innerHTML = `
        <div class="container mt-5">
            <h2>Подборка видео с котами!</h2>
            ${Carousel(catsGifs)}
            <button class="btn btn-secondary mt-3" onclick="renderMainPage()">Назад на главную</button>
        </div>
    `;
}
